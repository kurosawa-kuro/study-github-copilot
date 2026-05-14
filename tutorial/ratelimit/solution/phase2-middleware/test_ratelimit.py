"""Phase 2 で追加されるレートリミット test.

conftest.py の `client` fixture が `limit=5 / window=60` で構築している前提。
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_within_limit_returns_200(client: TestClient, auth_headers: dict[str, str]) -> None:
    for i in range(5):
        resp = client.get("/users/u-001", headers=auth_headers)
        assert resp.status_code == 200, f"iteration {i} should pass"


def test_exceeds_limit_returns_429_with_retry_after(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    for _ in range(5):
        client.get("/users/u-001", headers=auth_headers)

    resp = client.get("/users/u-001", headers=auth_headers)
    assert resp.status_code == 429
    assert resp.json() == {"detail": "rate limit exceeded"}
    assert resp.headers.get("Retry-After") == "60"


def test_health_is_not_ratelimited(client: TestClient) -> None:
    for _ in range(100):
        resp = client.get("/health")
        assert resp.status_code == 200


def test_separate_users_have_independent_counters(client: TestClient) -> None:
    headers_a = {"Authorization": "Bearer u-001"}
    headers_b = {"Authorization": "Bearer u-002"}

    for _ in range(5):
        client.get("/users/u-001", headers=headers_a)

    # u-001 は上限到達済み、u-002 は別カウンタなので通る
    resp_a = client.get("/users/u-001", headers=headers_a)
    resp_b = client.get("/users/u-002", headers=headers_b)
    assert resp_a.status_code == 429
    assert resp_b.status_code == 200


def test_unauthorized_request_does_not_consume_counter(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    # auth が先に走るので、認証失敗は ratelimit カウンタを消費しない想定
    for _ in range(10):
        resp = client.get("/users/u-001")
        assert resp.status_code == 401

    # 認証済みリクエストは通常通り 5 回まで成功
    for i in range(5):
        resp = client.get("/users/u-001", headers=auth_headers)
        assert resp.status_code == 200, f"iteration {i}"
