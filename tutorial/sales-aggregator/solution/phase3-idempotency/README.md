# Phase 3: 冪等性（二重投入防止）

## 目的

Phase 2 で残った `[BREAKING]`（同じ CSV を 2 回流すと二重計上）を解消する。
`idempotency_key`（既定: 入力ファイル名）で **取り込み済みか** を Redis Set に記録し、
2 回目以降の取り込みはスキップする。

## 変更ファイル

| パス | 種別 | 概要 | このディレクトリ内の成果物 |
|---|---|---|---|
| `src/salesagg/aggregator.py` | 変更 | `IdempotentStore` クラスを追加 | `aggregator.py` |
| `src/salesagg/main.py` | 変更 | CLI に `--idempotency-key` 追加、`--reset` を冪等マーカーも巻き込み | `main.py` |
| `tests/conftest.py` | 変更 | Phase 2 と同一 | `conftest.py` |
| `tests/test_idempotency.py` | 新規 | 二重投入防止・明示キー上書きのテスト | `test_idempotency.py` |

## 公開インタフェース

```python
class IdempotentStore:
    def __init__(self, kv: RedisKV) -> None: ...
    def is_processed(self, idempotency_key: str) -> bool: ...
    def try_mark_processed(self, idempotency_key: str) -> bool: ...
    def reset(self) -> None: ...
```

## 完了条件

- 機能条件: 同じ CSV を 2 回流しても累積値が変化しない（冪等）
- 機能条件: `--idempotency-key` で明示指定すれば、同じファイルでも別キーなら取り込まれる
- 機能条件: `--reset` で累積と冪等マーカーの両方がクリアされる
- テスト条件: `tests/test_idempotency.py` 全パス、既存テスト全パス
- 検証コマンド: `make verify`

## ロールバック手順

- `git revert HEAD`（Phase 2 状態に戻る、累積マージは継続動作）

## 注意 [OUT-OF-SCOPE]

- ファイル内容で重複判定する場合（同じ内容で別名のファイル）は別途ハッシュ化が必要。本 Phase ではファイル名 / 明示キー前提
- 冪等マーカーの TTL は無期限（無限に増える可能性は `[QUESTION]`、本 Phase では先送り）

## 引き継ぎ JSON

`../handoff-jsons/phase3.json` を参照。
