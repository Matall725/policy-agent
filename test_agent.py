from types import SimpleNamespace

import pytest

from agent import PolicyAgent


class FakeCompletions:
    def __init__(self, responses, fail_structured=False):
        self.responses = list(responses)
        self.calls = []
        self.fail_structured = fail_structured

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail_structured and "response_format" in kwargs:
            raise RuntimeError("response_format not supported")
        content = self.responses.pop(0)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class FakeClient:
    def __init__(self, responses, fail_structured=False):
        self.chat = SimpleNamespace(
            completions=FakeCompletions(responses, fail_structured)
        )


def make_agent(responses, fail_structured=False):
    agent = PolicyAgent("http://localhost", "key", "test-model")
    agent._client = FakeClient(responses, fail_structured)
    return agent


VALID_POLICY = (
    '{"policy_name": "测试政策", "support_target": "企业",'
    ' "benefits": "补贴", "deadline": "2026-01-01",'
    ' "requirements": [], "materials": []}'
)


def test_extract_policy_parses_fenced_json():
    agent = make_agent(["```json\n" + VALID_POLICY + "\n```"])
    result = agent.extract_policy("一些政策文本")
    assert result["policy_name"] == "测试政策"


def test_extract_policy_falls_back_to_text_mode():
    agent = make_agent([VALID_POLICY], fail_structured=True)
    result = agent.extract_policy("一些政策文本")
    assert result["policy_name"] == "测试政策"
    # First attempt used response_format, second did not.
    assert len(agent._client.chat.completions.calls) == 2
    assert "response_format" in agent._client.chat.completions.calls[0]
    assert "response_format" not in agent._client.chat.completions.calls[1]


def test_extract_policy_retries_on_invalid_json():
    agent = make_agent(["这不是 JSON", VALID_POLICY])
    result = agent.extract_policy("一些政策文本")
    assert result["policy_name"] == "测试政策"
    assert len(agent._client.chat.completions.calls) == 2


def test_extract_policy_raises_when_retry_also_fails():
    agent = make_agent(["bad", "still bad"])
    from parsers import LLMParseError

    with pytest.raises(LLMParseError):
        agent.extract_policy("一些政策文本")


def test_match_policy_returns_validated_result():
    match_json = (
        '{"match_score": 90, "summary": "符合", "eligible": true,'
        ' "unmet_requirements": [], "action_plan": ["提交申请"]}'
    )
    agent = make_agent([match_json])
    result = agent.match_policy({"policy_name": "x"}, {"req_1": {"answer": "是"}})
    assert result["match_score"] == 90
    assert result["eligible"] is True


def test_forced_structured_output_raises_on_failure():
    agent = make_agent([VALID_POLICY], fail_structured=True)
    agent.supports_structured_output = True
    with pytest.raises(RuntimeError):
        agent.extract_policy("一些政策文本")
