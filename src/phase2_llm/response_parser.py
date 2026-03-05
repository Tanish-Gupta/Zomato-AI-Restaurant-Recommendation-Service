"""Parse LLM response into structured recommendation data."""

import json
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ResponseParseError(Exception):
    """Raised when LLM response cannot be parsed as valid recommendations."""


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON object or array from text that may contain markdown or extra text.

    Handles:
    - Raw JSON
    - Text wrapped in ```json ... ```
    - Text with leading/trailing non-JSON content
    """
    text = (text or "").strip()
    if not text:
        raise ResponseParseError("Empty response text")

    # Try to find ```json ... ``` or ``` ... ```
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if code_block:
        text = code_block.group(1).strip()

    # Find first { and last }
    start = text.find("{")
    if start == -1:
        raise ResponseParseError("No JSON object found in response")
    depth = 0
    end = -1
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        raise ResponseParseError("Unbalanced braces in response")
    return text[start : end + 1]


def parse_recommendations_response(raw_response: str) -> Dict[str, Any]:
    """
    Parse the raw LLM response into a structured dict.

    Expected shape:
    {
      "recommendations": [
        {
          "name": str,
          "cuisine": str,
          "location": str,
          "rating": float,
          "price_range": str,
          "reason": str
        }
      ],
      "summary": str
    }

    Args:
        raw_response: Raw string returned by the LLM.

    Returns:
        Dict with "recommendations" (list of dicts) and "summary" (str).

    Raises:
        ResponseParseError: If parsing fails.
    """
    try:
        json_str = extract_json_from_text(raw_response)
        data = json.loads(json_str)
    except (json.JSONDecodeError, ResponseParseError) as e:
        logger.warning("Parse error: %s. Input snippet: %s", e, (raw_response or "")[:500])
        if isinstance(e, ResponseParseError):
            raise
        raise ResponseParseError(f"Invalid JSON in response: {e}") from e

    if not isinstance(data, dict):
        raise ResponseParseError("Response root must be a JSON object")

    recommendations = data.get("recommendations")
    if recommendations is None:
        recommendations = data.get("recommendation", [])
    if not isinstance(recommendations, list):
        recommendations = []

    summary = data.get("summary", "")
    if not isinstance(summary, str):
        summary = str(summary)

    normalized = []
    for i, rec in enumerate(recommendations):
        if not isinstance(rec, dict):
            continue
        normalized.append(
            {
                "name": _get_str(rec, "name", default="Unknown"),
                "cuisine": _get_str(rec, "cuisine", default=""),
                "location": _get_str(rec, "location", default=""),
                "rating": _get_float(rec, "rating"),
                "price_range": _get_str(rec, "price_range", default=""),
                "reason": _get_str(rec, "reason", default=""),
            }
        )

    return {
        "recommendations": normalized,
        "summary": summary.strip(),
    }


def _get_str(obj: Dict[str, Any], key: str, default: str = "") -> str:
    val = obj.get(key)
    if val is None:
        return default
    return str(val).strip()


def _get_float(obj: Dict[str, Any], key: str) -> float:
    val = obj.get(key)
    if val is None:
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0
