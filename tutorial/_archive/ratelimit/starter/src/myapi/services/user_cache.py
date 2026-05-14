from __future__ import annotations

from typing import Any

from myapi.core.redis_client import UserCacheRedis

# NOTE: チュートリアル用のインメモリ DB. 本物の DB を立てる代わりの fixture 相当.
# 読み取り専用前提で運用するため、テストで mutate しないこと.
_FAKE_DB: dict[str, dict[str, Any]] = {
    "u-001": {"id": "u-001", "name": "Alice", "email": "alice@example.com"},
    "u-002": {"id": "u-002", "name": "Bob", "email": "bob@example.com"},
}


def fetch_user(user_id: str, cache: UserCacheRedis) -> dict[str, Any] | None:
    cached = cache.get_user(user_id)
    if cached is not None:
        return cached
    fresh = _FAKE_DB.get(user_id)
    if fresh is None:
        return None
    cache.set_user_with_ttl(user_id, fresh)
    return fresh
