"""Phase 1 成果物: 汎用 Redis KV ラッパ.

集計の永続化に必要な最小 API のみを公開する.
"""

from __future__ import annotations

from typing import Any, Protocol, cast

import redis


class RedisKV(Protocol):
    def hget(self, key: str, field: str) -> str | None: ...
    def hincrby(self, key: str, field: str, amount: int) -> int: ...
    def hgetall(self, key: str) -> dict[str, str]: ...
    def sismember(self, key: str, member: str) -> bool: ...
    def sadd(self, key: str, member: str) -> int: ...
    def keys(self, pattern: str) -> list[str]: ...
    def delete(self, *keys: str) -> int: ...


class RedisKVImpl:
    # NOTE: redis-py の sync API は型上 Awaitable[X] | X を返すため、
    # 各メソッドで cast して同期結果を確定させる.
    def __init__(self, client: redis.Redis | None = None) -> None:
        self._c = client if client is not None else redis.Redis(decode_responses=True)

    def hget(self, key: str, field: str) -> str | None:
        v = cast("str | None", self._c.hget(key, field))
        return v

    def hincrby(self, key: str, field: str, amount: int) -> int:
        return cast("int", self._c.hincrby(key, field, amount))

    def hgetall(self, key: str) -> dict[str, str]:
        raw = cast("dict[Any, Any]", self._c.hgetall(key))
        return {str(k): str(v) for k, v in raw.items()}

    def sismember(self, key: str, member: str) -> bool:
        return bool(cast("int", self._c.sismember(key, member)))

    def sadd(self, key: str, member: str) -> int:
        return cast("int", self._c.sadd(key, member))

    def keys(self, pattern: str) -> list[str]:
        raw = cast("list[Any]", self._c.keys(pattern))
        return [str(k) for k in raw]

    def delete(self, *keys: str) -> int:
        if not keys:
            return 0
        return cast("int", self._c.delete(*keys))
