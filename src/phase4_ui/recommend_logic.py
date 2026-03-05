"""Recommendation logic for the UI (no Gradio dependency). Used by Gradio app and tests."""

import logging
from typing import List, Optional, Tuple

from src.phase3_api.recommendation import RecommendationService
from src.phase3_api.schemas import RecommendationRequest

logger = logging.getLogger(__name__)

_service: Optional[RecommendationService] = None


def get_service() -> RecommendationService:
    global _service
    if _service is None:
        _service = RecommendationService()
        _service._repo.initialize()
    return _service


def get_cuisines() -> List[str]:
    try:
        return ["Any"] + get_service()._repo.get_unique_cuisines()
    except Exception as e:
        logger.exception("get_cuisines failed")
        return ["Any"]


def get_locations() -> List[str]:
    try:
        return ["Any"] + get_service()._repo.get_unique_locations()
    except Exception as e:
        logger.exception("get_locations failed")
        return ["Any"]


def recommend(
    cuisine: Optional[str],
    location: Optional[str],
    price_range: Optional[str],
    min_rating: Optional[float],
    num_recommendations: int,
    additional_preferences: str,
) -> Tuple[str, str]:
    """Call recommendation service and return (results_md, summary)."""
    if not cuisine or cuisine == "Any":
        cuisine = None
    if not location or location == "Any":
        location = None
    if not price_range or price_range == "Any":
        price_range = None
    try:
        svc = get_service()
        req = RecommendationRequest(
            cuisine=cuisine,
            location=location,
            price_range=price_range,
            min_rating=min_rating,
            num_recommendations=num_recommendations,
            additional_preferences=additional_preferences or "",
        )
        resp = svc.get_recommendations(req)
    except Exception as e:
        logger.exception("recommend failed")
        return f"**Error:** {e}", ""

    lines = []
    for i, r in enumerate(resp.recommendations, 1):
        lines.append(f"### {i}. {r.name}")
        lines.append(f"- **Cuisine:** {r.cuisine} | **Location:** {r.location}")
        lines.append(f"- **Rating:** {r.rating} | **Price:** {r.price_range}")
        if r.reason:
            lines.append(f"- *{r.reason}*")
        lines.append("")
    results_md = "\n".join(lines) if lines else "*No recommendations.*"
    return results_md, resp.summary
