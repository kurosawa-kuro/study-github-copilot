"""User キャッシュ専用クライアント (Phase 1 後の姿).

Phase 1 で汎用 `RedisKV` を抽出し、`UserCacheRedis` は KV 層に委譲するだけになった。
外部 API (`get_user` / `set_user_with_ttl` / `invalidate_user`) は不変。
"""

from __future__ import annotations

import json
from typing import Any

from myapi.core.config import get_settings
from myapi.core.redis_kv import RedisKV, RedisKVImpl

_USER_KEY_PREFIX = "app:user"


class UserCacheRedis:
    def __init__(self, kv: RedisKV | None = None) -> None:
        self._kv: RedisKV = kv if kv is not None else RedisKVImpl()
        self._ttl = get_settings().user_cache_ttl_seconds

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        raw = self._kv.get(f"{_USER_KEY_PREFIX}:{user_id}")
        if raw is None:
            return None
        return json.loads(raw)

    def set_user_with_ttl(self, user_id: str, payload: dict[str, Any]) -> None:
        self._kv.set(
            f"{_USER_KEY_PREFIX}:{user_id}",
            json.dumps(payload),
            ttl_seconds=self._ttl,
        )

    def invalidate_user(self, user_id: str) -> None:
        self._kv.delete(f"{_USER_KEY_PREFIX}:{user_id}")
