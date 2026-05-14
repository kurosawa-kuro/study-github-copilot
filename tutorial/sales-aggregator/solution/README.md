# solution/

模範解答。Phase ごとに 1 ディレクトリ = 1 コミット相当。
各 Phase ディレクトリには **その Phase 完了時点の完全成果物**（コード + テスト + conftest）が配置されている。

## Phase 構成

| Phase | 目的 | 主な変更 |
|---|---|---|
| 1 | Redis KV 抽出 | `core/redis_kv.py` で汎用 KV ラッパを導入。aggregator はまだ Redis を使わない |
| 2 | 累積マージ | `CumulativeStore` を追加し、CLI を累積モードに切替。**この時点では二重投入で二重計上される** |
| 3 | 冪等性 | `IdempotentStore` で `idempotency_key` ベースの二重投入抑止 |

## 各 Phase ディレクトリの中身

| ファイル | 意味 |
|---|---|
| `README.md` | 目的・変更ファイル一覧・完了条件・検証コマンド・ロールバック手順 |
| `*.py` | starter ツリーに配置すべき完全成果物（パスは README の表を参照） |
| `conftest.py` | 各 Phase 完了時点の `tests/conftest.py` 全体像 |
| `test_*.py` | 各 Phase で追加・変更されたテストの完全版 |

## 引き継ぎ JSON

`handoff-jsons/phase1.json` 〜 `phase3.json` にサンプル。Step 4 完了時に受講者が出す JSON 例。

## 使い方

- 受講者は **見ない**（解答を先に見ると学習効果がゼロ）
- 各 Phase の `README.md` に完了条件・検証コマンド・ロールバック手順が揃っている
