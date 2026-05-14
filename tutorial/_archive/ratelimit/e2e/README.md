# E2E 動作確認ハーネス

Phase 3 完了後の **Step 5-A 統合検証** で使う実行スクリプト。
受講者が「動くレートリミッタ」を体感し、Step 5-A の検証コマンドとして実行結果を引き継ぎに貼る。

## 前提

- 受講者の starter ツリーで Phase 1〜3 が完了している（solution と等価な状態）
- `docker compose`（または `docker-compose`）が使える
- `curl` / `bash` が使える

## 起動手順

```bash
# 1. Redis 起動 (別ターミナル or -d)
cd tutorial/ratelimit/e2e
docker compose up -d

# 2. myapi 起動 (別ターミナル、ratelimit を 5 req / 10s に絞る)
cd tutorial/ratelimit/starter
MYAPI_REDIS_HOST=localhost \
MYAPI_RATELIMIT__LIMIT=5 \
MYAPI_RATELIMIT__WINDOW_SECONDS=10 \
  uv run uvicorn myapi.main:app --port 8000

# 3. シナリオ実行 (最初のターミナルに戻る)
cd tutorial/ratelimit/e2e
bash scenarios.sh
```

## シナリオ一覧

| # | 内容 | 期待 |
|---|---|---|
| 1 | 認証済 `/users/u-001` × 5 回 | 全部 200、`X-RateLimit-Remaining` が 4→0 |
| 2 | 6 回目 | 429 + `Retry-After: 10` + `X-RateLimit-Remaining: 0` |
| 3 | `/health` × 50 回 | 全部 200、ヘッダなし（除外対象） |
| 4 | 別 user_id (`u-002`) | 200（カウンタ独立） |
| 5 | 認証なし `/users/u-001` | 401（カウンタ非消費） |
| 6 | 10 秒待機後に再度叩く | 200（窓リセット） |

すべて pass で `All scenarios passed.` が出る。失敗時は該当シナリオ番号と理由が stderr に出る。

## 環境変数で変更可能

| 変数 | デフォルト | 用途 |
|---|---|---|
| `BASE_URL` | `http://localhost:8000` | myapi のエンドポイント |
| `EXPECTED_LIMIT` | `5` | Phase 3 の `MYAPI_RATELIMIT__LIMIT` と揃える |
| `WINDOW_SECONDS` | `10` | Phase 3 の `MYAPI_RATELIMIT__WINDOW_SECONDS` と揃える |
| `TOKEN_A` / `TOKEN_B` | `u-001` / `u-002` | 識別子 |

## 後片付け

```bash
docker compose down
# myapi は Ctrl-C で停止
```

## Step 5-A 引き継ぎでの使い方

`scenarios.sh` の出力（`OK: ...` × 6 行）を Step 5-A の引き継ぎ JSON の
`e2e_results` フィールドに貼り付ける。失敗があった場合は該当 Phase に差し戻し。

## 既知の注意

- シナリオ 6 はリアルタイムで 10 秒待つ。CI では `WINDOW_SECONDS=2` 等に短縮して使う
- Redis を `compose up` し直さず再実行すると、シナリオ 1 で 429 が出る。`docker compose down && docker compose up -d` で初期化
