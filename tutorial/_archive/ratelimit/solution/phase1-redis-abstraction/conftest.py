"""Phase 1 完了時の conftest.py 全体像.

Phase 1 で `RedisKVImpl` が増えたので fixture を追加。
`UserCacheRedis` は `kv=` 引数を受けるようになったため、
`user_cache` fixture は `fake_kv` 経由で生成する。
"""

from __future__ import annotations

import fakeredis
import pytest
from fastapi.testclient import TestClient

from myapi.core.redis_client import UserCacheRedis
from myapi.core.redis_kv import RedisKVImpl
from myapi.main import create_app
from myapi.routers.users import get_cache


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
def client(user_cache: UserCacheRedis) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_cache] = lambda: user_cache
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer u-001"}
