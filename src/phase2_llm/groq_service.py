"""Groq LLM service for restaurant recommendations."""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from groq import Groq

from src.config import GROQ_API_KEY, GROQ_MODEL

from .prompts import SYSTEM_PROMPT, build_user_prompt, format_restaurants_for_prompt

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 1.0


class GroqServiceError(Exception):
    """Raised when Groq API call fails after retries or due to config."""


class GroqLLMService:
    """
    Service for calling Groq LLM to generate restaurant recommendations.
    Uses system + user prompts and parses JSON response.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = MAX_RETRIES,
    ):
        # Only use env when api_key is not passed; explicit "" means no key (for tests)
        if api_key is None:
            api_key = GROQ_API_KEY or ""
        self._api_key = (api_key or "").strip()
        self._model = model or GROQ_MODEL
        self._max_retries = max_retries
        self._client: Optional[Groq] = None

    def _get_client(self) -> Groq:
        if not self._api_key:
            raise GroqServiceError(
                "GROQ_API_KEY is not set. Set it in .env or pass api_key to GroqLLMService."
            )
        if self._client is None:
            self._client = Groq(api_key=self._api_key)
        return self._client

    def get_recommendations(
        self,
        formatted_restaurant_list: str,
        cuisine: Optional[str] = None,
        location: Optional[str] = None,
        price_range: Optional[str] = None,
        min_rating: Optional[float] = None,
        num_recommendations: int = 5,
        additional_preferences: str = "",
    ) -> str:
        """
        Call Groq LLM to get recommendation response text (JSON string).

        Args:
            formatted_restaurant_list: Pre-formatted list of restaurants for the prompt.
            cuisine: User cuisine preference.
            location: User location preference.
            price_range: User price range preference.
            min_rating: Minimum rating filter (for display in prompt).
            num_recommendations: Number of recommendations to ask for.
            additional_preferences: Free-text user preferences.

        Returns:
            Raw response text from the model (expected to be JSON).
        """
        import time

        user_content = build_user_prompt(
            cuisine=cuisine or "Any",
            location=location or "Any",
            price_range=price_range or "Any",
            min_rating=str(min_rating) if min_rating is not None else "Any",
            num_recommendations=num_recommendations,
            additional_preferences=additional_preferences or "",
            formatted_restaurant_list=formatted_restaurant_list,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        client = self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                response = client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2048,
                )
                content = response.choices[0].message.content
                if not content or not content.strip():
                    raise GroqServiceError("Empty response from Groq")
                return content.strip()
            except GroqServiceError:
                # Empty or config errors: do not retry (retries won't help)
                raise
            except Exception as e:
                last_error = e
                logger.warning(
                    "Groq API attempt %s/%s failed: %s",
                    attempt + 1,
                    self._max_retries,
                    e,
                )
                if attempt < self._max_retries - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))

        raise GroqServiceError(
            f"Groq API failed after {self._max_retries} attempts: {last_error}"
        ) from last_error

    def is_configured(self) -> bool:
        """Return True if API key is set and service can be used."""
        return bool(self._api_key)


def format_restaurants_from_repository(
    restaurants_df,
    column_mapping: Dict[str, Optional[str]],
) -> str:
    """
    Build formatted restaurant list for the prompt using repository column mapping.

    Args:
        restaurants_df: DataFrame from RestaurantRepository.filter() or similar.
        column_mapping: Dict with keys name, cuisine, location, rating, price.

    Returns:
        Multi-line string for the prompt.
    """
    name_col = column_mapping.get("name") or "name"
    cuisine_col = column_mapping.get("cuisine") or "cuisine"
    location_col = column_mapping.get("location") or "location"
    rating_col = column_mapping.get("rating") or "rating"
    price_col = column_mapping.get("price") or "price_range"

    return format_restaurants_for_prompt(
        restaurants_df,
        name_col=name_col,
        cuisine_col=cuisine_col,
        location_col=location_col,
        rating_col=rating_col,
        price_col=price_col,
        max_lines=50,
    )
