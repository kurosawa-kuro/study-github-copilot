# Phase 2: 累積マージ

## 目的

商品ごとの累積を Redis に保持し、毎日 CSV を流すたびに追加マージするモードを導入。
レポート出力は **累積後のスナップショット**。`--reset` で手動リセット可能。

## 変更ファイル

| パス | 種別 | 概要 | このディレクトリ内の成果物 |
|---|---|---|---|
| `src/salesagg/aggregator.py` | 変更 | `CumulativeStore` クラスを追加（既存 `aggregate` は維持） | `aggregator.py` |
| `src/salesagg/main.py` | 変更 | CLI に累積マージモード組込（`--reset` 追加） | `main.py` |
| `tests/conftest.py` | 変更 | `sample_csv_day2` fixture 追加 | `conftest.py` |
| `tests/test_cumulative.py` | 新規 | 累積マージ・リセット・CLI 統合のテスト | `test_cumulative.py` |

## 公開インタフェース

```python
class CumulativeStore:
    def __init__(self, kv: RedisKV) -> None: ...
    def merge(self, batch: Iterable[ProductTotal]) -> None: ...
    def snapshot(self) -> list[ProductTotal]: ...
    def reset(self) -> None: ...
```

## 完了条件

- 機能条件: 同じ CSV を 2 回流すと累積値が **2 倍** になる（= 冪等性は未実装、Phase 3 で対処）
- 機能条件: 別日の CSV を流すと累積される
- 機能条件: `--reset` 付与時、累積がクリアされてから新バッチが取り込まれる
- テスト条件: `tests/test_cumulative.py` 全パス、既存テスト全パス
- 検証コマンド: `make verify`

## ロールバック手順

- `git revert HEAD` で `aggregator.py` と `main.py` を Phase 1 状態に戻す

## 注意（次 Phase への引き継ぎ）

[BREAKING] **同じ CSV を 2 回投入すると二重計上される**。Phase 3 で idempotency key 機構を入れて対処する。

## 引き継ぎ JSON

`../handoff-jsons/phase2.json` を参照。
