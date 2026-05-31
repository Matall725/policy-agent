import json
import requests
import os
from openai import OpenAI

def load_prompt(filename):
    path = os.path.join(os.path.dirname(__file__), "prompts", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class PolicyAgent:
    def __init__(self, api_base, api_key, model_name):
        self.api_base = api_base
        self.api_key = api_key
        self.model_name = model_name
        self.extractor_prompt = load_prompt("extractor_prompt.md")
        self.matcher_prompt = load_prompt("matcher_prompt.md")

    def _get_client(self):
        return OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

    def extract_policy(self, policy_text):
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.extractor_prompt},
                    {"role": "user", "content": f"请解析以下政策文本：\n\n{policy_text}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"} if "gpt" in self.model_name or "deepseek" in self.model_name else None
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("`json"):
                content = content.split("`json")[1].split("`")[0].strip()
            elif content.startswith("`"):
                content = content.split("`")[1].split("`")[0].strip()
            return json.loads(content)
        except Exception as e:
            raise Exception(f"政策解析失败: {str(e)}")

    def match_policy(self, policy_json, user_answers):
        try:
            client = self._get_client()
            prompt_content = {
                "policy": policy_json,
                "user_answers": user_answers
            }
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.matcher_prompt},
                    {"role": "user", "content": f"请根据以下政策结构化数据和用户的实际回答，进行匹配度评估：\n\n{json.dumps(prompt_content, ensure_ascii=False, indent=2)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"} if "gpt" in self.model_name or "deepseek" in self.model_name else None
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("`json"):
                content = content.split("`json")[1].split("`")[0].strip()
            elif content.startswith("`"):
                content = content.split("`")[1].split("`")[0].strip()
            return json.loads(content)
        except Exception as e:
            raise Exception(f"匹配度评估失败: {str(e)}")
