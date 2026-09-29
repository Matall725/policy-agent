import pytest

from parsers import (
    LLMParseError,
    SchemaValidationError,
    extract_json_object,
    parse_and_validate,
    strip_markdown_wrapping,
)
from schemas import PolicyExtraction


def test_strip_markdown_fenced_json():
    raw = '```json\n{"a": 1}\n```'
    assert strip_markdown_wrapping(raw) == '{"a": 1}'


def test_strip_markdown_plain_text_unchanged():
    raw = '{"a": 1}'
    assert strip_markdown_wrapping(raw) == '{"a": 1}'


def test_extract_plain_json():
    assert extract_json_object('{"a": 1}') == {"a": 1}


def test_extract_fenced_json():
    raw = '```json\n{"a": 1, "b": [2, 3]}\n```'
    assert extract_json_object(raw) == {"a": 1, "b": [2, 3]}


def test_extract_json_with_surrounding_prose():
    raw = '好的，以下是结果：\n{"a": 1}\n希望有帮助。'
    assert extract_json_object(raw) == {"a": 1}


def test_extract_nested_json():
    raw = '{"outer": {"inner": {"x": 1}}}'
    assert extract_json_object(raw) == {"outer": {"inner": {"x": 1}}}


def test_extract_json_ignores_braces_in_strings():
    raw = '{"note": "use {curly} braces", "ok": true}'
    assert extract_json_object(raw) == {"note": "use {curly} braces", "ok": True}


def test_extract_invalid_json_raises():
    with pytest.raises(LLMParseError):
        extract_json_object("no json here at all")


def test_parse_and_validate_success():
    raw = (
        '{"policy_name": "Test Policy", "deadline": "2026-01-01",'
        ' "requirements": [], "materials": []}'
    )
    result = parse_and_validate(raw, PolicyExtraction)
    assert result.policy_name == "Test Policy"
    assert result.deadline == "2026-01-01"


def test_parse_and_validate_raises_on_schema_mismatch():
    raw = '{"deadline": "2026-01-01"}'  # missing required policy_name
    with pytest.raises(SchemaValidationError):
        parse_and_validate(raw, PolicyExtraction)


def test_parse_and_validate_retry_recovers():
    calls = {"n": 0}

    def retry_fn(_previous: str) -> str:
        calls["n"] += 1
        return '{"policy_name": "Fixed", "requirements": [], "materials": []}'

    result = parse_and_validate(
        "not json", PolicyExtraction, max_retries=1, retry_fn=retry_fn
    )
    assert calls["n"] == 1
    assert result.policy_name == "Fixed"
