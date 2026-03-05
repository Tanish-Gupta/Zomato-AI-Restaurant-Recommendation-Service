"""Tests for Phase 4: User Interface."""

import pytest


class TestRecommendLogic:
    """Test recommendation logic without requiring Gradio."""

    def test_recommend_returns_two_strings(self):
        from src.phase4_ui.recommend_logic import recommend

        results, summary = recommend(
            cuisine="Any",
            location="Any",
            price_range="Any",
            min_rating=None,
            num_recommendations=2,
            additional_preferences="",
        )
        assert isinstance(results, str)
        assert isinstance(summary, str)

    def test_recommend_with_filters_returns_something(self):
        from src.phase4_ui.recommend_logic import recommend

        results, summary = recommend(
            cuisine="Any",
            location="Any",
            price_range="Any",
            min_rating=3.0,
            num_recommendations=3,
            additional_preferences="",
        )
        assert isinstance(results, str)
        assert isinstance(summary, str)
        assert len(results) > 0 or "No" in results or "recommendation" in summary.lower()

    def test_get_cuisines_returns_list_with_any(self):
        from src.phase4_ui.recommend_logic import get_cuisines

        cuisines = get_cuisines()
        assert isinstance(cuisines, list)
        assert "Any" in cuisines

    def test_get_locations_returns_list_with_any(self):
        from src.phase4_ui.recommend_logic import get_locations

        locations = get_locations()
        assert isinstance(locations, list)
        assert "Any" in locations


class TestGradioApp:
    """Test Gradio UI build (skipped if Gradio has import errors)."""

    def test_build_ui_returns_blocks(self):
        gr = pytest.importorskip("gradio")
        from src.phase4_ui.gradio_app import build_ui

        demo = build_ui()
        assert demo is not None
        assert isinstance(demo, gr.Blocks)
