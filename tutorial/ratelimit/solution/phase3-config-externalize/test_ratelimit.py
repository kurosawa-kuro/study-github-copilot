"""Phase 3 で追加されるヘッダ・設定外出しの test.

Phase 2 の test_ratelimit.py に「ヘッダ検証」「設定差し替え」のテストを追加した版。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from myapi.core.config import RatelimitSettings
from myapi.core.redis_kv import RedisKVImpl
from myapi.main import create_app
from myapi.routers.users import get_cache


def test_ratelimit_headers_on_success(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/users/u-001", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["X-RateLimit-Limit"] == "5"
    assert resp.headers["X-RateLimit-Remaining"] == "4"
    assert resp.headers["X-RateLimit-Reset"] == "60"


def test_ratelimit_headers_decrement(client: TestClient, auth_headers: dict[str, str]) -> None:
    remaining_values: list[int] = []
    for _ in range(5):
        resp = client.get("/users/u-001", headers=auth_headers)
        remaining_values.append(int(resp.headers["X-RateLimit-Remaining"]))
    assert remaining_values == [4, 3, 2, 1, 0]


def test_429_includes_all_headers(client: TestClient, auth_headers: dict[str, str]) -> None:
    for _ in range(5):
        client.get("/users/u-001", headers=auth_headers)

    resp = client.get("/users/u-001", headers=auth_headers)
    assert resp.status_code == 429
    assert resp.headers["Retry-After"] == "60"
    assert resp.headers["X-RateLimit-Limit"] == "5"
    assert resp.headers["X-RateLimit-Remaining"] == "0"


def test_custom_config_overrides_defaults(
    fake_kv: RedisKVImpl, user_cache, auth_headers: dict[str, str]
) -> None:
    cfg = RatelimitSettings(limit=2, window_seconds=30, target_path_prefixes=("/users",))
    app = create_app(kv=fake_kv, cfg=cfg)
    app.dependency_overrides[get_cache] = lambda: user_cache
    test_client = TestClient(app)

    for _ in range(2):
        resp = test_client.get("/users/u-001", headers=auth_headers)
        assert resp.status_code == 200
    resp = test_client.get("/users/u-001", headers=auth_headers)
    assert resp.status_code == 429
    assert resp.headers["Retry-After"] == "30"


def test_target_path_prefixes_filter(
    fake_kv: RedisKVImpl, user_cache, auth_headers: dict[str, str]
) -> None:
    cfg = RatelimitSettings(limit=2, window_seconds=60, target_path_prefixes=("/orders",))
    app = create_app(kv=fake_kv, cfg=cfg)
    app.dependency_overrides[get_cache] = lambda: user_cache
    test_client = TestClient(app)

    # /users は対象外なので 100 回叩いても通る
    for _ in range(10):
        resp = test_client.get("/users/u-001", headers=auth_headers)
        assert resp.status_code == 200
        assert "X-RateLimit-Limit" not in resp.headers
