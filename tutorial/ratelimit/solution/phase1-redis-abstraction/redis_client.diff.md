# `core/redis_client.py` 差分（要旨）

`UserCacheRedis` を `RedisKV` 委譲に書き換える。外部 API は不変。

```python
from myapi.core.redis_kv import RedisKV, RedisKVImpl

_USER_KEY_PREFIX = "app:user"


class UserCacheRedis:
    def __init__(self, kv: RedisKV | None = None) -> None:
        self._kv = kv or RedisKVImpl()
        self._ttl = get_settings().user_cache_ttl_seconds

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        raw = self._kv.get(f"{_USER_KEY_PREFIX}:{user_id}")
        return json.loads(raw) if raw is not None else None

    def set_user_with_ttl(self, user_id: str, payload: dict[str, Any]) -> None:
        self._kv.set(f"{_USER_KEY_PREFIX}:{user_id}", json.dumps(payload), ttl_seconds=self._ttl)

    def invalidate_user(self, user_id: str) -> None:
        self._kv.delete(f"{_USER_KEY_PREFIX}:{user_id}")
```

[BREAKING] なし — 既存呼び出し元 (`services/user_cache.py`, `routers/users.py`) は変更不要。
