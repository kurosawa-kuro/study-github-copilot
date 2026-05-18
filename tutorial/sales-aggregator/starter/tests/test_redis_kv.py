"""Phase 1 で追加される RedisKV のテスト."""

from __future__ import annotations

import fakeredis
import pytest

from salesagg.redis_kv import RedisKVImpl


def test_hincrby_creates_and_increments(fake_kv: RedisKVImpl) -> None:
    """hincrby で新規キーは作成、既存キーは加算."""
    assert fake_kv.hincrby("app:test", "qty", 3) == 3
    assert fake_kv.hincrby("app:test", "qty", 2) == 5


def test_hgetall_returns_all_fields(fake_kv: RedisKVImpl) -> None:
    """hgetall ですべてのフィールドを辞書で取得."""
    fake_kv.hincrby("app:test", "qty", 10)
    fake_kv.hincrby("app:test", "amount", 1500)
    assert fake_kv.hgetall("app:test") == {"qty": "10", "amount": "1500"}


def test_hget_missing_returns_none(fake_kv: RedisKVImpl) -> None:
    """hget で存在しないキーは None を返す."""
    assert fake_kv.hget("app:nope", "qty") is None


def test_hget_existing_field(fake_kv: RedisKVImpl) -> None:
    """hget で存在するフィールドは値を返す."""
    fake_kv.hincrby("app:test", "qty", 100)
    assert fake_kv.hget("app:test", "qty") == "100"


def test_set_membership(fake_kv: RedisKVImpl) -> None:
    """Set メンバーシップ: sismember/sadd の動作."""
    assert fake_kv.sismember("app:processed", "file-a") is False
    assert fake_kv.sadd("app:processed", "file-a") == 1
    assert fake_kv.sismember("app:processed", "file-a") is True
    # 同じメンバーの再追加は 0
    assert fake_kv.sadd("app:processed", "file-a") == 0


def test_keys_and_delete(fake_kv: RedisKVImpl) -> None:
    """keys パターンマッチングと delete."""
    fake_kv.hincrby("app:report:product:p-001", "qty", 1)
    fake_kv.hincrby("app:report:product:p-002", "qty", 1)
    found = sorted(fake_kv.keys("app:report:product:*"))
    assert found == ["app:report:product:p-001", "app:report:product:p-002"]
    assert fake_kv.delete(*found) == 2
    assert fake_kv.keys("app:report:product:*") == []


def test_delete_empty_keys_returns_zero(fake_kv: RedisKVImpl) -> None:
    """delete に空のキーリストを渡すと 0 を返す."""
    assert fake_kv.delete() == 0


def test_hgetall_empty_key(fake_kv: RedisKVImpl) -> None:
    """hgetall で存在しないキーは空辞書を返す."""
    assert fake_kv.hgetall("app:nonexistent") == {}


def test_keys_no_match(fake_kv: RedisKVImpl) -> None:
    """keys パターンにマッチするキーがない場合は空リスト."""
    fake_kv.hincrby("app:report:product:p-001", "qty", 1)
    assert fake_kv.keys("app:other:*") == []


def test_init_accepts_custom_client(fake_redis: fakeredis.FakeRedis) -> None:
    """カスタム redis.Redis インスタンスを受け入れ."""
    from salesagg.redis_kv import RedisKVImpl
    
    kv = RedisKVImpl(client=fake_redis)
    assert kv is not None
    kv.hincrby("test", "field", 1)
    assert kv.hget("test", "field") == "1"


def test_init_without_client_creates_default() -> None:
    """client=None でデフォルト redis.Redis() を作成（本番環境）."""
    # NOTE: 本番環境では Redis が起動していることが前提
    # テスト環境では実際の Redis に接続する可能性があるため、
    # ここではスキップまたは mock を使用することを推奨
    from salesagg.redis_kv import RedisKVImpl
    import redis
    
    try:
        # 実環境 Redis がない場合はスキップ
        kv = RedisKVImpl()
        kv.hincrby("test", "field", 1)
        kv.delete("test")
    except redis.ConnectionError:
        # [QUESTION] 本番デプロイ時に Redis が必須の旨をドキュメント化すべき
        pytest.skip("Redis not available")
