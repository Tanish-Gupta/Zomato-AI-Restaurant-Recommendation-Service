"""Pydantic schemas for API request/response validation."""

import math
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer


class RecommendationRequest(BaseModel):
    """Request body for the /recommend endpoint."""

    cuisine: Optional[str] = Field(None, description="e.g. Italian, Indian, Chinese")
    location: Optional[str] = Field(None, description="e.g. Connaught Place, Koramangala")
    price_range: Optional[str] = Field(None, description="low, medium, high, very_high")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating 0-5")
    num_recommendations: int = Field(5, ge=1, le=20, description="Number of recommendations")
    additional_preferences: str = Field("", description="Free text for extra context")


class RestaurantRecommendation(BaseModel):
    """Single restaurant recommendation from the LLM."""

    name: str
    cuisine: str
    location: str
    rating: float
    price_range: str
    reason: str = ""

    @field_serializer("rating")
    def serialize_rating(self, v: float):
        if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
            return 0.0
        return round(float(v), 2)


class RecommendationResponse(BaseModel):
    """Response from the /recommend endpoint."""

    recommendations: List[RestaurantRecommendation] = Field(default_factory=list)
    summary: str = ""
    query_context: dict = Field(default_factory=dict)
