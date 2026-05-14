# Phase 1: Redis KV ラッパ抽出

## 目的

集計の永続化に備えて、redis-py への直接依存を 1 箇所に閉じ込める汎用 `RedisKV` を導入する。
Phase 2 以降で集計ストアが KV 層に乗る土台。**既存挙動は変えない**（aggregator はまだ Redis を使わない）。

## 変更ファイル

| パス | 種別 | 概要 | このディレクトリ内の成果物 |
|---|---|---|---|
| `src/salesagg/redis_kv.py` | 新規 | `Protocol` で抽象化した KV ラッパ | `redis_kv.py` |
| `tests/conftest.py` | 変更 | `fake_kv` fixture を追加 | `conftest.py` |
| `tests/test_redis_kv.py` | 新規 | `RedisKV` の正常系・異常系 | `test_redis_kv.py` |

## 公開インタフェース

```python
class RedisKV(Protocol):
    def hget(self, key: str, field: str) -> str | None: ...
    def hincrby(self, key: str, field: str, amount: int) -> int: ...
    def hgetall(self, key: str) -> dict[str, str]: ...
    def sismember(self, key: str, member: str) -> bool: ...
    def sadd(self, key: str, member: str) -> int: ...
    def keys(self, pattern: str) -> list[str]: ...
    def delete(self, *keys: str) -> int: ...
```

## 完了条件

- 機能条件: `salesagg --input ... --output ...` が従来通り動く（既存テスト全パス）
- テスト条件: `tests/test_redis_kv.py` が全パス
- 検証コマンド: `make verify`

## ロールバック手順

- `git revert HEAD`（aggregator は触っていないので影響範囲は新規ファイルのみ）

## 引き継ぎ JSON

`../handoff-jsons/phase1.json` を参照。
