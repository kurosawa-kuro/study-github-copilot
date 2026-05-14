"""Phase 2 完了時の conftest.py 全体像.

`client` fixture が `create_app` に `kv=` と小さな `limit=` を渡すように変わる。
Phase 3 で settings 経由になると `limit=` 直渡しは消える。
"""

from __future__ import annotations

import fakeredis
import pytest
from fastapi.testclient import TestClient

from myapi.core.redis_client import UserCacheRedis
from myapi.core.redis_kv import RedisKVImpl
from myapi.main import create_app
from myapi.routers.users import get_cache

TEST_LIMIT = 5
TEST_WINDOW_SECONDS = 60


@pytest.fixture
def fake_redis() -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def fake_kv(fake_redis: fakeredis.FakeRedis) -> RedisKVImpl:
    return RedisKVImpl(client=fake_redis)


@pytest.fixture
def user_cache(fake_kv: RedisKVImpl) -> UserCacheRedis:
    return UserCacheRedis(kv=fake_kv)


@pytest.fixture
def client(user_cache: UserCacheRedis, fake_kv: RedisKVImpl) -> TestClient:
    app = create_app(kv=fake_kv, limit=TEST_LIMIT, window_seconds=TEST_WINDOW_SECONDS)
    app.dependency_overrides[get_cache] = lambda: user_cache
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer u-001"}
