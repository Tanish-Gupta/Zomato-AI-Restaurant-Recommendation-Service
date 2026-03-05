"""Simple in-memory response cache for recommendation requests."""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Default: 5 minutes TTL, max 500 entries
DEFAULT_TTL_SECONDS = 300
DEFAULT_MAX_SIZE = 500


class ResponseCache:
    """In-memory cache for recommendation responses. Not thread-safe."""

    def __init__(
        self,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        max_size: int = DEFAULT_MAX_SIZE,
    ):
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: Dict[str, Tuple[float, Any]] = {}  # key -> (expiry_ts, value)

    def _key(self, request_dict: dict) -> str:
        canonical = json.dumps(request_dict, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def get(self, request_dict: dict) -> Optional[Any]:
        k = self._key(request_dict)
        if k not in self._store:
            return None
        expiry, value = self._store[k]
        if time.time() > expiry:
            del self._store[k]
            return None
        return value

    def set(self, request_dict: dict, value: Any) -> None:
        if len(self._store) >= self._max_size:
            self._evict_expired()
            if len(self._store) >= self._max_size:
                # Remove oldest (first inserted)
                first = next(iter(self._store))
                del self._store[first]
        k = self._key(request_dict)
        self._store[k] = (time.time() + self._ttl, value)

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [k for k, (exp, _) in self._store.items() if now > exp]
        for k in expired:
            del self._store[k]

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)
