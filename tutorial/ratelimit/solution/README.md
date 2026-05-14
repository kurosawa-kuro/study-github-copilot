# solution/

模範解答。Phase ごとに 1 ディレクトリ = 1 コミット相当。

## Phase 構成

| Phase | 目的 | 主な変更 |
|---|---|---|
| 1 | Redis 接続抽象化 | `core/redis_client.py` から汎用 KV 層 (`core/redis_kv.py`) を抽出、既存の `UserCacheRedis` は KV に委譲 |
| 2 | レートリミット middleware 実装 | `core/ratelimit.py` (固定窓、`INCR + EXPIRE`)、`main.py` で middleware 登録（auth より後 / `/health` は除外） |
| 3 | 設定外出し | `RatelimitSettings` を `core/config.py` に追加、上限・窓幅・対象 path を環境変数化、`X-RateLimit-*` ヘッダ整備 |

## 引き継ぎ JSON

`handoff-jsons/phase1.json` 〜 `phase3.json` にサンプル。Step 4 完了時に受講者が出す JSON 例。

## 使い方

- 受講者は **見ない**（解答を先に見ると学習効果がゼロ）
- ファシリは Step 4 のレビュー時、戻り先判定の正解確認に使う
- 各 Phase ディレクトリの `README.md` に diff サマリと完了条件・検証コマンドが入っている
