"""Phase 2 成果物: 固定窓レートリミッタ.

INCR で当該窓のカウンタを増やし、初回 (=1) のみ EXPIRE で TTL を打つ。
race condition は許容範囲（max で 1 リクエスト溢れる程度）.
"""

from __future__ import annotations

from dataclasses import dataclass

from myapi.core.redis_kv import RedisKV


_KEY_PREFIX = "app:ratelimit"


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_in_seconds: int


class RateLimiter:
    def __init__(self, kv: RedisKV, limit: int, window_seconds: int) -> None:
        self._kv = kv
        self._limit = limit
        self._window = window_seconds

    def check(self, identifier: str) -> RateLimitResult:
        key = f"{_KEY_PREFIX}:{identifier}"
        count = self._kv.incr(key)
        if count == 1:
            self._kv.expire(key, self._window)
        remaining = max(0, self._limit - count)
        return RateLimitResult(
            allowed=count <= self._limit,
            remaining=remaining,
            reset_in_seconds=self._window,
        )
