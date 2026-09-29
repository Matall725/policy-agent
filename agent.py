import json
import logging
import os
from openai import OpenAI

from parsers import LLMParseError, SchemaValidationError, parse_and_validate
from schemas import MatchResult, PolicyExtraction

logger = logging.getLogger(__name__)

def load_prompt(filename):
    path = os.path.join(os.path.dirname(__file__), "prompts", filename)
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()

class PolicyAgent:
    def __init__(
        self,
        api_base,
        api_key,
        model_name,
        supports_structured_output=None,
    ):
        self.api_base = api_base
        self.api_key = api_key
        self.model_name = model_name
        # None: try structured output then fall back. True: force it.
        # False: disable it. This replaces the fragile model-name check.
        self.supports_structured_output = supports_structured_output
        self.extractor_prompt = load_prompt("extractor_prompt.md")
        self.matcher_prompt = load_prompt("matcher_prompt.md")
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
            )
        return self._client

    def _call_llm(self, system_prompt, user_content, temperature=0.1):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        client = self._get_client()
        if self.supports_structured_output is not False:
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                return response.choices[0].message.content.strip()
            except Exception as exc:
                if self.supports_structured_output is True:
                    raise RuntimeError(
                        f"structured output call failed: {exc}"
                    ) from exc
                logger.debug(
                    "structured output unavailable (%s); using text mode", exc
                )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    def _parse_with_retry(self, raw_text, schema, system_prompt):
        try:
            return parse_and_validate(raw_text, schema, max_retries=0)
        except (LLMParseError, SchemaValidationError) as exc:
            logger.warning("initial parse failed (%s); retrying once", exc)
            correction = (
                "你之前的回复无法被解析为合法 JSON，或未通过字段校验。"
                f"以下是原始回复：\n\n{raw_text}\n\n"
                "请只输出修正后的合法 JSON，不要包含任何其他文字。"
            )
            corrected = self._call_llm(
                system_prompt=system_prompt,
                user_content=correction,
                temperature=0.0,
            )
            return parse_and_validate(corrected, schema, max_retries=0)

    def extract_policy(self, policy_text):
        raw = self._call_llm(
            self.extractor_prompt,
            f"请解析以下政策文本：\n\n{policy_text}",
        )
        result = self._parse_with_retry(raw, PolicyExtraction, self.extractor_prompt)
        return result.model_dump()

    def match_policy(self, policy_json, user_answers):
        payload = {"policy": policy_json, "user_answers": user_answers}
        raw = self._call_llm(
            self.matcher_prompt,
            "请根据以下政策结构化数据和用户的实际回答，进行匹配度评估：\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2),
        )
        result = self._parse_with_retry(raw, MatchResult, self.matcher_prompt)
        return result.model_dump()
