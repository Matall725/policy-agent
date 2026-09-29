"""Robust parsing of raw LLM responses into validated structured data."""

import json
import re
from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class LLMParseError(Exception):
    """Raised when an LLM response cannot be parsed into valid JSON."""


class SchemaValidationError(Exception):
    """Raised when parsed JSON fails schema validation."""


def strip_markdown_wrapping(text: str) -> str:
    """Remove markdown code fences that some models wrap JSON in."""
    fenced_pattern = re.compile(
        r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL
    )
    match = fenced_pattern.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def extract_json_object(text: str) -> Any:
    """
    Extract the first valid JSON object from an LLM response.

    Handles:
    - Plain JSON
    - JSON inside ```json ... ``` fences
    - JSON with leading/trailing prose text
    """
    stripped = strip_markdown_wrapping(text)

    # Try the whole string first.
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Fall back to scanning for the first balanced { ... } block.
    start = stripped.find("{")
    if start == -1:
        raise LLMParseError("no JSON object found in LLM response")

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(stripped)):
        ch = stripped[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = stripped[start : i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        # Might be a false start; keep scanning.
                        continue

    raise LLMParseError("no valid JSON object could be extracted from response")


def parse_and_validate(
    raw_text: str,
    schema: Type[T],
    max_retries: int = 1,
    retry_fn: Callable[[str], str] = None,
) -> T:
    """
    Parse raw LLM text and validate against a Pydantic schema.

    If parsing or validation fails and retry_fn is provided, it is called
    with the raw response and its result is retried. max_retries controls
    the number of retry attempts.
    """
    text = raw_text
    last_error: Exception = None
    for attempt in range(1 + max_retries):
        try:
            json_obj = extract_json_object(text)
            return schema.model_validate(json_obj)
        except LLMParseError as e:
            last_error = e
        except ValidationError as e:
            last_error = SchemaValidationError(
                f"schema validation failed: {e}"
            )

        if attempt < max_retries and retry_fn is not None:
            text = retry_fn(text)
        else:
            break

    if isinstance(last_error, LLMParseError):
        raise last_error
    raise last_error
