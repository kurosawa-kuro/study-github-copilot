from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_order_ok(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/orders/o-100", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "shipped"


def test_health_no_auth(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
