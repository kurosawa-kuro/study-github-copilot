"""Phase 1 成果物: 汎用 Redis KV ラッパ.

User キャッシュ / レートリミットの両方が依存する最小 API のみを公開する.
"""

from __future__ import annotations

from typing import Protocol

import redis

from myapi.core.config import get_settings


class RedisKV(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None: ...
    def incr(self, key: str) -> int: ...
    def expire(self, key: str, ttl_seconds: int) -> bool: ...
    def delete(self, key: str) -> None: ...


class RedisKVImpl:
    def __init__(self, client: redis.Redis | None = None) -> None:
        if client is None:
            s = get_settings()
            client = redis.Redis(host=s.redis_host, port=s.redis_port, db=s.redis_db, decode_responses=True)
        self._c = client

    def get(self, key: str) -> str | None:
        return self._c.get(key)

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        self._c.set(key, value, ex=ttl_seconds)

    def incr(self, key: str) -> int:
        return int(self._c.incr(key))

    def expire(self, key: str, ttl_seconds: int) -> bool:
        return bool(self._c.expire(key, ttl_seconds))

    def delete(self, key: str) -> None:
        self._c.delete(key)
