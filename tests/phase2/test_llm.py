"""Tests for Phase 2: Groq LLM Integration.

Unit tests run without GROQ_API_KEY. Integration test that calls the Groq API
is skipped unless GROQ_API_KEY is set (run with API key when ready).
"""

import os
import pytest
import pandas as pd

from src.phase2_llm.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
    format_restaurants_for_prompt,
)
from src.phase2_llm.response_parser import (
    ResponseParseError,
    extract_json_from_text,
    parse_recommendations_response,
)
from src.phase2_llm.groq_service import (
    GroqLLMService,
    GroqServiceError,
    format_restaurants_from_repository,
)


class TestPrompts:
    """Tests for prompt building (no API key required)."""

    def test_system_prompt_is_non_empty(self):
        assert SYSTEM_PROMPT
        assert "restaurant" in SYSTEM_PROMPT.lower()
        assert "JSON" in SYSTEM_PROMPT

    def test_build_user_prompt_defaults(self):
        prompt = build_user_prompt(formatted_restaurant_list="R1 | Italian | NYC | 4.5 | medium")
        assert "Any" in prompt
        assert "R1 | Italian | NYC | 4.5 | medium" in prompt
        assert "5" in prompt  # num_recommendations default

    def test_build_user_prompt_with_preferences(self):
        prompt = build_user_prompt(
            cuisine="Indian",
            location="Delhi",
            price_range="medium",
            min_rating="4.0",
            num_recommendations=3,
            additional_preferences="vegetarian",
            formatted_restaurant_list="Restaurant A | Indian | Delhi | 4.2 | medium",
        )
        assert "Indian" in prompt
        assert "Delhi" in prompt
        assert "medium" in prompt
        assert "4.0" in prompt
        assert "3" in prompt
        assert "vegetarian" in prompt
        assert "Restaurant A" in prompt

    def test_format_restaurants_for_prompt_empty_df(self):
        df = pd.DataFrame()
        out = format_restaurants_for_prompt(
            df,
            name_col="name",
            cuisine_col="cuisine",
            location_col="location",
            rating_col="rating",
            price_col="price",
        )
        assert out == "No restaurants available."

    def test_format_restaurants_for_prompt_with_data(self):
        df = pd.DataFrame({
            "name": ["Cafe A", "Cafe B"],
            "cuisine": ["Italian", "Indian"],
            "location": ["NYC", "Mumbai"],
            "rating": [4.5, 4.0],
            "price": [2, 3],
        })
        out = format_restaurants_for_prompt(
            df,
            name_col="name",
            cuisine_col="cuisine",
            location_col="location",
            rating_col="rating",
            price_col="price",
        )
        assert "Cafe A" in out
        assert "Cafe B" in out
        assert "Italian" in out
        assert "4.5" in out


class TestResponseParser:
    """Tests for response parsing (no API key required)."""

    def test_extract_json_from_raw_json(self):
        text = '{"recommendations": [], "summary": "Done"}'
        assert extract_json_from_text(text) == text

    def test_extract_json_from_markdown_block(self):
        text = 'Here is the result:\n```json\n{"recommendations": [], "summary": "Done"}\n```'
        extracted = extract_json_from_text(text)
        assert "recommendations" in extracted
        assert "summary" in extracted

    def test_extract_json_raises_on_empty(self):
        with pytest.raises(ResponseParseError):
            extract_json_from_text("")
        with pytest.raises(ResponseParseError):
            extract_json_from_text("   ")

    def test_extract_json_raises_on_no_brace(self):
        with pytest.raises(ResponseParseError):
            extract_json_from_text("no json here")

    def test_parse_recommendations_response_valid(self):
        raw = '{"recommendations": [{"name": "R1", "cuisine": "Italian", "location": "NYC", "rating": 4.5, "price_range": "medium", "reason": "Great food"}], "summary": "Top pick."}'
        result = parse_recommendations_response(raw)
        assert result["summary"] == "Top pick."
        assert len(result["recommendations"]) == 1
        assert result["recommendations"][0]["name"] == "R1"
        assert result["recommendations"][0]["rating"] == 4.5

    def test_parse_recommendations_response_empty_list(self):
        raw = '{"recommendations": [], "summary": "No matches."}'
        result = parse_recommendations_response(raw)
        assert result["recommendations"] == []
        assert result["summary"] == "No matches."

    def test_parse_recommendations_response_normalizes_types(self):
        raw = '{"recommendations": [{"name": "R1", "cuisine": "X", "location": "Y", "rating": "4.0", "price_range": "medium", "reason": "Good"}], "summary": ""}'
        result = parse_recommendations_response(raw)
        assert result["recommendations"][0]["rating"] == 4.0

    def test_parse_recommendations_response_invalid_json_raises(self):
        with pytest.raises(ResponseParseError):
            parse_recommendations_response("not json at all")


class TestGroqServiceNoApiKey:
    """Tests for GroqLLMService that do not require API key."""

    def test_is_configured_false_when_no_key(self):
        svc = GroqLLMService(api_key="")
        assert svc.is_configured() is False

    def test_is_configured_true_when_key_set(self):
        svc = GroqLLMService(api_key="dummy_key")
        assert svc.is_configured() is True

    def test_get_recommendations_raises_when_no_key(self):
        svc = GroqLLMService(api_key="")
        with pytest.raises(GroqServiceError) as exc_info:
            svc.get_recommendations(
                formatted_restaurant_list="R1 | Italian | NYC | 4.5 | medium",
            )
        assert "GROQ_API_KEY" in str(exc_info.value)


class TestFormatRestaurantsFromRepository:
    """Tests for formatting repository DataFrame for prompt."""

    def test_format_with_column_mapping(self):
        df = pd.DataFrame({
            "restaurant_name": ["A", "B"],
            "cuisines": ["Italian", "Indian"],
            "location": ["NYC", "Mumbai"],
            "aggregate_rating": [4.5, 4.0],
            "price_range": [2, 3],
        })
        mapping = {
            "name": "restaurant_name",
            "cuisine": "cuisines",
            "location": "location",
            "rating": "aggregate_rating",
            "price": "price_range",
        }
        out = format_restaurants_from_repository(df, mapping)
        assert "A" in out
        assert "B" in out
        assert "Italian" in out


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set; run with API key to execute integration test",
)
class TestGroqIntegration:
    """Integration tests that call Groq API. Run only when GROQ_API_KEY is set."""

    def test_get_recommendations_returns_json_like_response(self):
        from src.phase2_llm.groq_service import GroqServiceError

        svc = GroqLLMService()
        try:
            raw = svc.get_recommendations(
                formatted_restaurant_list="Test Restaurant | Indian | Delhi | 4.5 | medium",
                cuisine="Indian",
                num_recommendations=2,
            )
        except GroqServiceError as e:
            pytest.skip(f"Groq API unavailable (network/auth): {e}")
        assert raw
        parsed = parse_recommendations_response(raw)
        assert "recommendations" in parsed
        assert "summary" in parsed
        assert isinstance(parsed["recommendations"], list)
