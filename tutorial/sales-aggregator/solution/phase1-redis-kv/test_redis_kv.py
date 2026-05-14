"""Phase 1 で追加される RedisKV のテスト."""

from __future__ import annotations

from salesagg.redis_kv import RedisKVImpl


def test_hincrby_creates_and_increments(fake_kv: RedisKVImpl) -> None:
    assert fake_kv.hincrby("app:test", "qty", 3) == 3
    assert fake_kv.hincrby("app:test", "qty", 2) == 5


def test_hgetall_returns_all_fields(fake_kv: RedisKVImpl) -> None:
    fake_kv.hincrby("app:test", "qty", 10)
    fake_kv.hincrby("app:test", "amount", 1500)
    assert fake_kv.hgetall("app:test") == {"qty": "10", "amount": "1500"}


def test_hget_missing_returns_none(fake_kv: RedisKVImpl) -> None:
    assert fake_kv.hget("app:nope", "qty") is None


def test_set_membership(fake_kv: RedisKVImpl) -> None:
    assert fake_kv.sismember("app:processed", "file-a") is False
    assert fake_kv.sadd("app:processed", "file-a") == 1
    assert fake_kv.sismember("app:processed", "file-a") is True
    # 同じメンバーの再追加は 0
    assert fake_kv.sadd("app:processed", "file-a") == 0


def test_keys_and_delete(fake_kv: RedisKVImpl) -> None:
    fake_kv.hincrby("app:report:product:p-001", "qty", 1)
    fake_kv.hincrby("app:report:product:p-002", "qty", 1)
    found = sorted(fake_kv.keys("app:report:product:*"))
    assert found == ["app:report:product:p-001", "app:report:product:p-002"]
    assert fake_kv.delete(*found) == 2
    assert fake_kv.keys("app:report:product:*") == []
