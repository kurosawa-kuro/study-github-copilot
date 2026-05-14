# solution/

模範解答。Phase ごとに 1 ディレクトリ = 1 コミット相当。
各 Phase ディレクトリには **その Phase 完了時点の完全成果物**（コード + テスト + conftest）が配置されている。

## Phase 構成

| Phase | 目的 | 主な変更 |
|---|---|---|
| 1 | Redis 接続抽象化 | `core/redis_client.py` から汎用 KV 層 (`core/redis_kv.py`) を抽出、既存の `UserCacheRedis` は KV に委譲 |
| 2 | レートリミット middleware 実装 | `core/ratelimit.py` (固定窓、`INCR + EXPIRE`)、`main.py` で middleware 登録（auth → ratelimit / `/health` は除外） |
| 3 | 設定外出し | `RatelimitSettings` を `core/config.py` に追加、上限・窓幅・対象 path を環境変数化、`X-RateLimit-*` ヘッダ整備 |

## 各 Phase ディレクトリの中身

| ファイル | 意味 |
|---|---|
| `README.md` | 目的・変更ファイル一覧・完了条件・検証コマンド・ロールバック手順 |
| `<module>.py` | starter ツリーに配置すべき完全成果物。パスは README の表を参照 |
| `conftest.py` | 各 Phase 完了時点の `tests/conftest.py` 全体像 |
| `test_*.py` | 各 Phase で追加・変更されたテストの完全版 |

## 引き継ぎ JSON

`handoff-jsons/phase1.json` 〜 `phase3.json` にサンプル。Step 4 完了時に受講者が出す JSON 例。

## 使い方

- 受講者は **見ない**（解答を先に見ると学習効果がゼロ）
- ファシリは Step 4 のレビュー時、受講者の差分と各 Phase の完全成果物を直接比較できる
- 各 Phase の `README.md` に完了条件・検証コマンド・ロールバック手順が揃っている
