# Step 3 → Step 4 ループ ヒント

ネタバレを最小に抑えた「詰まったらここを見る」ヒント集。
**Phase 実装を始める前には読まない**（戻り先判定の練習にならなくなる）。

## 詰まったらレベル別に開く

### レベル 1: 自分のレビューで違和感がある（× / △ が出た）

Step 4 の **戻り先判定表** をもう一度見て、自分の問題がどの分類か判定する:

| 問題 | 戻り先 |
|---|---|
| 軽微なバグ・テスト漏れ | Step 3 |
| 完了条件不備・分割ミス | Step 2 |
| 要件・既存矛盾 | Step 1 |
| 設計欠陥 | Step 0-B |
| 要件曖昧 | Step 0-A |

戻り先を **明記してから** 修正に着手する。

### レベル 2: どの戻り先かも分からない

Phase ごとの「ありがちな問題」を順に確認:

#### Phase 1（Redis 抽象化）

- `UserCacheRedis.__init__` のシグネチャを変えた場合、呼び出し元（`services/user_cache.py`, `routers/users.py`, `tests/conftest.py`）が壊れていないか
- 既存テスト（`test_users.py` / `test_orders.py`）が全パスしているか

#### Phase 2（middleware 実装）★ 戻り先判定が起きやすい

ありがちな症状とその戻り先（自分の状況が当てはまるか確認）:

| 症状 | 戻り先 | ヒント |
|---|---|---|
| `/health` がレートリミット対象になっている | Step 3 | 除外パスの判定漏れ |
| middleware が auth より先に走り、user_id が未設定 | Step 2 | 完了条件に「順序」が無かった |
| `INCR` で初回 EXPIRE タイミングが race | Step 3 | `return == 1` のとき**だけ** EXPIRE する |
| `[BREAKING]`（gateway 二重制御）を出していない | Step 1 | Step 1 の影響範囲調査やり直し |
| 429 に `Retry-After` が無い | Step 3 | レスポンスヘッダ追加 |

#### Phase 3（設定外出し）

- 環境変数を変えてテストが通るか実演する（`MYAPI_RATELIMIT__LIMIT=5 uv run pytest ...`）
- ヘッダ命名（`X-RateLimit-*`）の IETF draft 準拠は `[OUT-OF-SCOPE]` で挙げる

### レベル 3: それでも詰まった

`facilitator-guide/05-step3-4-loop.md` を見る（**ネタバレあり**）。
ファシリ用ドキュメントなので最後の手段。

## 自学自習者向け重要ルール

- **戻り先判定 が一度も発生しない進行は学習効果が薄い**
- Phase 2 で「ふわっと完了条件を書いて Step 3 に進んだ」場合、middleware 順序問題で Step 2 戻りを **体験するべき**
- 仕掛けに気づいて Step 2 で予防できた場合、それは **上位の能力**（[final-rubric.md](final-rubric.md) で加点）
