"""Tests for Phase 3: API Development."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.phase3_api.schemas import RecommendationRequest, RecommendationResponse, RestaurantRecommendation


@pytest.fixture
def client():
    return TestClient(app)


class TestHealth:
    def test_health_returns_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "restaurant" in data["service"].lower()


class TestRoot:
    def test_root_returns_message(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "docs" in data


class TestCuisines:
    def test_cuisines_returns_list(self, client):
        # Uses real repo (may be slow on first run)
        r = client.get("/api/cuisines")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)


class TestLocations:
    def test_locations_returns_list(self, client):
        r = client.get("/api/locations")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)


class TestRecommend:
    def test_recommend_accepts_request_and_returns_200(self, client):
        payload = {
            "cuisine": "Indian",
            "num_recommendations": 2,
        }
        r = client.post("/api/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "recommendations" in data
        assert "summary" in data
        assert "query_context" in data
        assert isinstance(data["recommendations"], list)

    def test_recommend_with_empty_filters(self, client):
        payload = {"num_recommendations": 3}
        r = client.post("/api/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "recommendations" in data

    def test_recommend_validates_num_recommendations(self, client):
        payload = {"num_recommendations": 0}
        r = client.post("/api/recommend", json=payload)
        assert r.status_code == 422  # validation error

    def test_recommend_validates_min_rating_range(self, client):
        payload = {"min_rating": 10}  # max is 5
        r = client.post("/api/recommend", json=payload)
        assert r.status_code == 422


class TestSchemas:
    def test_recommendation_request_defaults(self):
        req = RecommendationRequest()
        assert req.num_recommendations == 5
        assert req.additional_preferences == ""

    def test_restaurant_recommendation_model(self):
        r = RestaurantRecommendation(
            name="Test",
            cuisine="Italian",
            location="NYC",
            rating=4.5,
            price_range="medium",
            reason="Great food",
        )
        assert r.name == "Test"
        assert r.rating == 4.5
