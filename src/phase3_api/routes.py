"""FastAPI route definitions."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request

from src.phase3_api.recommendation import RecommendationService
from src.phase3_api.schemas import RecommendationRequest, RecommendationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["recommendations"])

# Lazy-initialized service (uses Phase 1 repo + Phase 2 LLM)
_service: Optional[RecommendationService] = None

# Phase 5: optional cache and rate limiter
try:
    from src.phase5_optimization.caching import ResponseCache
    from src.phase5_optimization.rate_limit import RateLimiter
    _cache = ResponseCache(ttl_seconds=300, max_size=500)
    _rate_limiter = RateLimiter(requests_per_window=60, window_seconds=60)
except ImportError:
    _cache = None
    _rate_limiter = None


def get_recommendation_service() -> RecommendationService:
    global _service
    if _service is None:
        _service = RecommendationService()
        _service._repo.initialize()
    return _service


@router.get("/health")
def health():
    """Health check for load balancers and monitoring."""
    return {"status": "ok", "service": "restaurant-recommendation"}


@router.get("/cuisines", response_model=List[str])
def list_cuisines():
    """Return list of unique cuisines in the dataset."""
    try:
        svc = get_recommendation_service()
        return svc._repo.get_unique_cuisines()
    except Exception as e:
        logger.exception("list_cuisines failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/locations", response_model=List[str])
def list_locations():
    """Return list of unique locations in the dataset."""
    try:
        svc = get_recommendation_service()
        return svc._repo.get_unique_locations()
    except Exception as e:
        logger.exception("list_locations failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest, request: Request):
    """Get restaurant recommendations based on preferences."""
    if _rate_limiter is not None:
        client = request.client.host if request.client else "default"
        if not _rate_limiter.is_allowed(client):
            raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    if _cache is not None:
        key_dict = req.model_dump(exclude_none=False)
        cached = _cache.get(key_dict)
        if cached is not None:
            return RecommendationResponse.model_validate(cached)
    try:
        svc = get_recommendation_service()
        resp = svc.get_recommendations(req)
        if _cache is not None:
            _cache.set(req.model_dump(exclude_none=False), resp.model_dump())
        return resp
    except Exception as e:
        logger.exception("recommend failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
