"""Phase 3 完了時の conftest.py 全体像.

`client` fixture が `RatelimitSettings` を直接渡す形になり、
Phase 2 の `limit=` / `window_seconds=` 直渡しは消える。
"""

from __future__ import annotations

import fakeredis
import pytest
from fastapi.testclient import TestClient

from myapi.core.config import RatelimitSettings
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
def ratelimit_cfg() -> RatelimitSettings:
    return RatelimitSettings(
        limit=5,
        window_seconds=60,
        target_path_prefixes=("/users", "/orders"),
    )


@pytest.fixture
def client(
    user_cache: UserCacheRedis,
    fake_kv: RedisKVImpl,
    ratelimit_cfg: RatelimitSettings,
) -> TestClient:
    app = create_app(kv=fake_kv, cfg=ratelimit_cfg)
    app.dependency_overrides[get_cache] = lambda: user_cache
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer u-001"}
