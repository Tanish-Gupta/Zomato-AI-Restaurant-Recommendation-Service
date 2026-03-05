"""Tests for Phase 5: Caching, rate limiting, CLI."""

import pytest


class TestResponseCache:
    def test_get_miss_returns_none(self):
        from src.phase5_optimization.caching import ResponseCache

        c = ResponseCache(ttl_seconds=60, max_size=10)
        assert c.get({"a": 1}) is None

    def test_set_and_get(self):
        from src.phase5_optimization.caching import ResponseCache

        c = ResponseCache(ttl_seconds=60, max_size=10)
        c.set({"cuisine": "Indian"}, {"recommendations": [], "summary": "Done"})
        assert c.get({"cuisine": "Indian"}) == {"recommendations": [], "summary": "Done"}

    def test_different_keys_dont_collide(self):
        from src.phase5_optimization.caching import ResponseCache

        c = ResponseCache(ttl_seconds=60, max_size=10)
        c.set({"a": 1}, "v1")
        c.set({"a": 2}, "v2")
        assert c.get({"a": 1}) == "v1"
        assert c.get({"a": 2}) == "v2"

    def test_clear(self):
        from src.phase5_optimization.caching import ResponseCache

        c = ResponseCache(ttl_seconds=60, max_size=10)
        c.set({"x": 1}, "v")
        c.clear()
        assert c.get({"x": 1}) is None
        assert c.size() == 0


class TestRateLimiter:
    def test_allowed_within_limit(self):
        from src.phase5_optimization.rate_limit import RateLimiter

        r = RateLimiter(requests_per_window=2, window_seconds=60)
        assert r.is_allowed("u1") is True
        assert r.is_allowed("u1") is True
        assert r.is_allowed("u1") is False

    def test_different_keys_separate(self):
        from src.phase5_optimization.rate_limit import RateLimiter

        r = RateLimiter(requests_per_window=1, window_seconds=60)
        assert r.is_allowed("u1") is True
        assert r.is_allowed("u2") is True
        assert r.is_allowed("u1") is False

    def test_remaining(self):
        from src.phase5_optimization.rate_limit import RateLimiter

        r = RateLimiter(requests_per_window=3, window_seconds=60)
        assert r.remaining("u1") == 3
        r.is_allowed("u1")
        assert r.remaining("u1") == 2


class TestCLI:
    def test_cli_help(self):
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "src.phase5_optimization.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "cuisine" in result.stdout or "recommendations" in result.stdout.lower()

    def test_cli_runs_and_returns_zero(self):
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "src.phase5_optimization.cli", "-n", "1", "--json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert "recommendations" in data
        assert "summary" in data
