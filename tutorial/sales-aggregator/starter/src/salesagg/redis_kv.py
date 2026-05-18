"""Phase 1 成果物: 汎用 Redis KV ラッパ.

集計の永続化に必要な最小 API のみを公開する.
"""

from __future__ import annotations

from typing import Any, Protocol, cast

import redis


class RedisKV(Protocol):
    """集計・冪等性に必要な最小 API."""

    def hget(self, key: str, field: str) -> str | None: ...

    def hincrby(self, key: str, field: str, amount: int) -> int: ...

    def hgetall(self, key: str) -> dict[str, str]: ...

    def sismember(self, key: str, member: str) -> bool: ...

    def sadd(self, key: str, member: str) -> int: ...

    def keys(self, pattern: str) -> list[str]: ...

    def delete(self, *keys: str) -> int: ...


class RedisKVImpl:
    """redis-py の同期 API をラップ.

    redis-py の戻り値をキャストして同期結果を確定させる.
    """

    def __init__(self, client: redis.Redis | None = None) -> None:
        self._c = client if client is not None else redis.Redis(decode_responses=True)

    def hget(self, key: str, field: str) -> str | None:
        """Hash から単一フィールドを取得."""
        v = cast("str | None", self._c.hget(key, field))
        return v

    def hincrby(self, key: str, field: str, amount: int) -> int:
        """Hash フィールドを整数で加算（キー新規作成時は amount）."""
        return cast("int", self._c.hincrby(key, field, amount))

    def hgetall(self, key: str) -> dict[str, str]:
        """Hash のすべてのフィールドをスナップショット取得."""
        raw = cast("dict[Any, Any]", self._c.hgetall(key))
        return {str(k): str(v) for k, v in raw.items()}

    def sismember(self, key: str, member: str) -> bool:
        """Set のメンバーシップをチェック."""
        return bool(cast("int", self._c.sismember(key, member)))

    def sadd(self, key: str, member: str) -> int:
        """Set にメンバーを追加（1=新規, 0=既存）."""
        return cast("int", self._c.sadd(key, member))

    def keys(self, pattern: str) -> list[str]:
        """パターンマッチするすべてのキーを取得."""
        raw = cast("list[Any]", self._c.keys(pattern))
        return [str(k) for k in raw]

    def delete(self, *keys: str) -> int:
        """複数のキーを削除（削除数を返す）."""
        if not keys:
            return 0
        return cast("int", self._c.delete(*keys))
