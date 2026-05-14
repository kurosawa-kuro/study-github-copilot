"""後方互換性検出器.

`UserCacheRedis` の外部 API は不変、というのが本チュートリアル全体の前提
(`CLAUDE.md` / Phase 1 README に明記). Phase 1 で内部を `RedisKV` 委譲に書き換えても、
以下のテストが緑のままであれば外部 API は壊れていない.

これらが壊れたら `[BREAKING]` として報告し、Step 4 のレビューで戻り先判定する.
"""

from __future__ import annotations

import inspect

from myapi.core.redis_client import UserCacheRedis


def test_user_cache_has_expected_public_methods() -> None:
    expected = {"get_user", "set_user_with_ttl", "invalidate_user"}
    actual = {name for name in dir(UserCacheRedis) if not name.startswith("_")}
    assert expected.issubset(actual), f"missing public methods: {expected - actual}"


def test_get_user_signature_is_stable() -> None:
    sig = inspect.signature(UserCacheRedis.get_user)
    params = list(sig.parameters.values())
    assert [p.name for p in params] == ["self", "user_id"]


def test_set_user_with_ttl_signature_is_stable() -> None:
    sig = inspect.signature(UserCacheRedis.set_user_with_ttl)
    params = list(sig.parameters.values())
    assert [p.name for p in params] == ["self", "user_id", "payload"]


def test_users_endpoint_stable_contract(client, auth_headers) -> None:
    """`/users/{id}` の契約 (200 / 404 / 401) が壊れていないか."""
    ok = client.get("/users/u-001", headers=auth_headers)
    assert ok.status_code == 200
    assert "name" in ok.json()

    not_found = client.get("/users/unknown-id", headers=auth_headers)
    assert not_found.status_code == 404

    unauth = client.get("/users/u-001")
    assert unauth.status_code == 401
