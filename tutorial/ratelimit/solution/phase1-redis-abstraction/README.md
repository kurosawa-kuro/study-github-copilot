# Phase 1: Redis 接続抽象化

## 目的

`UserCacheRedis` が User キャッシュの語彙に密結合しているため、レートリミット用に汎用 KV 層
（`incr`, `expire`, `get`, `set`, `delete`）を持つ `RedisKV` を抽出する。
既存の `UserCacheRedis` は `RedisKV` に委譲する形に置き換える（外部 API は不変）。

## 変更ファイル

| パス | 種別 | 概要 | 想定行数 |
|---|---|---|---|
| `src/myapi/core/redis_kv.py` | 新規 | 汎用 KV ラッパ（`Protocol` で抽象化） | 約 50 |
| `src/myapi/core/redis_client.py` | 変更 | `UserCacheRedis` を `RedisKV` 委譲に書き換え | 約 40 |
| `tests/test_redis_kv.py` | 新規 | `RedisKV` の正常系・異常系・境界値 | 約 60 |
| `tests/conftest.py` | 変更 | `redis_kv` fixture を追加（fakeredis ラップ） | 約 10 |

## 公開インタフェース

```python
class RedisKV(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None: ...
    def incr(self, key: str) -> int: ...
    def expire(self, key: str, ttl_seconds: int) -> bool: ...
    def delete(self, key: str) -> None: ...
```

## 完了条件

- 機能条件: `/users/{id}` が従来通り 200 / 404 を返す（既存テスト全パス）
- テスト条件: `tests/test_redis_kv.py` 全パス、既存テストも全パス
- 検証コマンド: `uv run pytest -q`

## ロールバック手順

- `git revert HEAD` （`UserCacheRedis` の旧実装に戻す）

## 引き継ぎ JSON

`../handoff-jsons/phase1.json` を参照。
