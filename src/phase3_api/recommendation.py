"""Recommendation orchestration: data + LLM + parsing."""

import logging
from typing import Any, Dict, List, Optional

from src.phase1_data import RestaurantRepository
from src.phase2_llm import (
    GroqLLMService,
    GroqServiceError,
    format_restaurants_from_repository,
    parse_recommendations_response,
    ResponseParseError,
)

from .schemas import RecommendationRequest, RecommendationResponse, RestaurantRecommendation

logger = logging.getLogger(__name__)

# Max candidates to send to LLM (keep prompt size bounded)
MAX_CANDIDATES_FOR_LLM = 50


class RecommendationService:
    """Orchestrates repository filter -> LLM -> parse into API response."""

    def __init__(
        self,
        repository: Optional[RestaurantRepository] = None,
        llm_service: Optional[GroqLLMService] = None,
    ):
        self._repo = repository or RestaurantRepository()
        self._llm = llm_service or GroqLLMService()

    @staticmethod
    def _normalize_filter(value: Optional[str]) -> Optional[str]:
        """Treat 'Any', empty string, etc. as no filter (None)."""
        if value is None:
            return None
        v = (value or "").strip().lower()
        if v in ("", "any", "all", "none"):
            return None
        return value.strip() or None

    def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Get restaurant recommendations: filter data, call LLM, parse and return.
        """
        cuisine = self._normalize_filter(request.cuisine)
        location = self._normalize_filter(request.location)
        price_range = self._normalize_filter(request.price_range)
        # Treat min_rating 0 as "no minimum" so we don't filter by rating
        min_rating = request.min_rating if (request.min_rating is not None and request.min_rating > 0) else None

        # 1. Filter restaurants from repository
        filtered_df = self._repo.filter(
            cuisine=cuisine,
            location=location,
            min_rating=min_rating,
            price_range=price_range,
            limit=MAX_CANDIDATES_FOR_LLM,
        )

        if filtered_df.empty:
            return RecommendationResponse(
                recommendations=[],
                summary="No restaurants match your criteria. Try relaxing filters (e.g. cuisine or location).",
                query_context=request.model_dump(exclude_none=True),
            )

        # 2. Format restaurant list for prompt
        formatted_list = format_restaurants_from_repository(
            filtered_df,
            self._repo._column_mapping,
        )

        # 3. Call LLM (if configured)
        if not self._llm.is_configured():
            # Fallback: return top N from filtered list without LLM reasoning
            return self._fallback_recommendations(request, filtered_df)

        try:
            raw = self._llm.get_recommendations(
                formatted_restaurant_list=formatted_list,
                cuisine=cuisine or request.cuisine,
                location=location or request.location,
                price_range=price_range or request.price_range,
                min_rating=request.min_rating,
                num_recommendations=request.num_recommendations,
                additional_preferences=request.additional_preferences or "",
            )
            parsed = parse_recommendations_response(raw)
        except (GroqServiceError, ResponseParseError) as e:
            logger.warning("LLM failed, using fallback: %s", e)
            return self._fallback_recommendations(request, filtered_df)

        # 4. Build response
        recs = [
            RestaurantRecommendation(
                name=r.get("name", "Unknown"),
                cuisine=r.get("cuisine", ""),
                location=r.get("location", ""),
                rating=float(r.get("rating", 0)),
                price_range=r.get("price_range", ""),
                reason=r.get("reason", ""),
            )
            for r in parsed["recommendations"]
        ]
        return RecommendationResponse(
            recommendations=recs,
            summary=parsed.get("summary", ""),
            query_context=request.model_dump(exclude_none=True),
        )

    def _fallback_recommendations(
        self,
        request: RecommendationRequest,
        df,
    ) -> RecommendationResponse:
        """Return top N by rating when LLM is not available or fails."""
        name_col = self._repo._column_mapping.get("name") or "name"
        cuisine_col = self._repo._column_mapping.get("cuisine") or "cuisine"
        location_col = self._repo._column_mapping.get("location") or "location"
        rating_col = self._repo._column_mapping.get("rating") or "rating"
        price_col = self._repo._column_mapping.get("price") or "price_range"
        price_cat_col = f"{price_col}_category"

        import pandas as pd

        df = df.copy()
        df["_rating_num"] = pd.to_numeric(df.get(rating_col, 0), errors="coerce")
        top = df.nlargest(request.num_recommendations, "_rating_num")

        recs: List[RestaurantRecommendation] = []
        for _, row in top.iterrows():
            price_val = row.get(price_cat_col, row.get(price_col, ""))
            recs.append(
                RestaurantRecommendation(
                    name=str(row.get(name_col, "Unknown"))[:100],
                    cuisine=str(row.get(cuisine_col, ""))[:100],
                    location=str(row.get(location_col, ""))[:100],
                    rating=float(row.get("_rating_num", 0)),
                    price_range=str(price_val)[:20],
                    reason="Top pick by rating (LLM unavailable).",
                )
            )
        return RecommendationResponse(
            recommendations=recs,
            summary="Recommendations by rating (Groq LLM not configured or failed).",
            query_context=request.model_dump(exclude_none=True),
        )
