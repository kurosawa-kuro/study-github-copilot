from __future__ import annotations

import fakeredis
import pytest
from fastapi.testclient import TestClient

from myapi.core.redis_client import UserCacheRedis
from myapi.main import create_app
from myapi.routers.users import get_cache


@pytest.fixture
def fake_redis() -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def user_cache(fake_redis: fakeredis.FakeRedis) -> UserCacheRedis:
    return UserCacheRedis(client=fake_redis)


@pytest.fixture
def client(user_cache: UserCacheRedis) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_cache] = lambda: user_cache
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer u-001"}
