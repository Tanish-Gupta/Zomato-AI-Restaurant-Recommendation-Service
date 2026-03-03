"""Phase 2: Groq LLM Integration - LLM service, prompts, and response parsing."""

from .groq_service import GroqLLMService, GroqServiceError, format_restaurants_from_repository
from .prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    build_user_prompt,
    format_restaurants_for_prompt,
)
from .response_parser import (
    ResponseParseError,
    extract_json_from_text,
    parse_recommendations_response,
)

__all__ = [
    "GroqLLMService",
    "GroqServiceError",
    "format_restaurants_from_repository",
    "SYSTEM_PROMPT",
    "USER_PROMPT_TEMPLATE",
    "build_user_prompt",
    "format_restaurants_for_prompt",
    "ResponseParseError",
    "extract_json_from_text",
    "parse_recommendations_response",
]
