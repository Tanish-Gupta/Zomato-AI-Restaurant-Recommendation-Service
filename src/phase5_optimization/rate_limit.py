"""Simple in-memory rate limiter."""

import time
from collections import defaultdict
from typing import Dict, List, Optional


class RateLimiter:
    """
    In-memory rate limiter: max N requests per window_seconds per key (e.g. per client_id).
    Not distributed; for single-process use.
    """

    def __init__(self, requests_per_window: int = 60, window_seconds: float = 60.0):
        self._limit = requests_per_window
        self._window = window_seconds
        self._counts: Dict[str, List[float]] = defaultdict(list)  # key -> list of request timestamps

    def is_allowed(self, key: str = "default") -> bool:
        """Return True if the request is allowed, and record it."""
        now = time.time()
        cutoff = now - self._window
        # Keep only timestamps within the window
        self._counts[key] = [t for t in self._counts[key] if t > cutoff]
        if len(self._counts[key]) >= self._limit:
            return False
        self._counts[key].append(now)
        return True

    def remaining(self, key: str = "default") -> int:
        """Return how many requests are left in the current window."""
        now = time.time()
        cutoff = now - self._window
        self._counts[key] = [t for t in self._counts[key] if t > cutoff]
        return max(0, self._limit - len(self._counts[key]))
