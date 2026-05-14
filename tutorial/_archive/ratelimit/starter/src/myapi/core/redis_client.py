"""User キャッシュ専用 Redis クライアント.

NOTE (intentional design smell):
- メソッドが User キャッシュの語彙 (get_user / set_user_with_ttl) に密結合している。
- レートリミット等の別ユースケースを足すときは、汎用 KV 層を抽出する必要がある。
"""

from __future__ import annotations

import json
from typing import Any

import redis

from myapi.core.config import get_settings

_USER_KEY_PREFIX = "app:user"


class UserCacheRedis:
    def __init__(self, client: redis.Redis | None = None) -> None:
        if client is None:
            settings = get_settings()
            client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
            )
        self._client = client
        self._ttl = get_settings().user_cache_ttl_seconds

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        raw = self._client.get(f"{_USER_KEY_PREFIX}:{user_id}")
        if raw is None:
            return None
        return json.loads(raw)

    def set_user_with_ttl(self, user_id: str, payload: dict[str, Any]) -> None:
        self._client.set(
            f"{_USER_KEY_PREFIX}:{user_id}",
            json.dumps(payload),
            ex=self._ttl,
        )

    def invalidate_user(self, user_id: str) -> None:
        self._client.delete(f"{_USER_KEY_PREFIX}:{user_id}")
