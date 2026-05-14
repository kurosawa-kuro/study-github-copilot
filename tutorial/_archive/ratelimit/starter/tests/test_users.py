from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_user_ok(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/users/u-001", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"


def test_get_user_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/users/unknown", headers=auth_headers)
    assert resp.status_code == 404


def test_get_user_unauthorized(client: TestClient) -> None:
    resp = client.get("/users/u-001")
    assert resp.status_code == 401
