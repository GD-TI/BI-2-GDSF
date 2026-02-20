from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import RLock
from typing import Any


@dataclass
class TTLCache:
    _cache: dict[str, Any] = field(default_factory=dict)
    _timestamps: dict[str, datetime] = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock)

    def get(self, key: str, ttl_seconds: int = 60) -> Any | None:
        with self._lock:
            if key not in self._cache:
                return None

            if datetime.now() - self._timestamps[key] > timedelta(seconds=ttl_seconds):
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
                return None

            return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.now()

    def clear(self, prefix: str | None = None) -> None:
        with self._lock:
            if prefix is None:
                self._cache.clear()
                self._timestamps.clear()
                return

            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_delete:
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)

    def generate_key(self, endpoint: str, params: dict[str, Any] | None = None) -> str:
        if params is None:
            return f"cache:{endpoint}"

        params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        return f"cache:{endpoint}:{params_hash}"

    def stats(self) -> list[dict[str, Any]]:
        now = datetime.now()
        with self._lock:
            return [
                {
                    "key": key,
                    "age_seconds": round((now - ts).total_seconds(), 2),
                    "created_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for key, ts in self._timestamps.items()
            ]
