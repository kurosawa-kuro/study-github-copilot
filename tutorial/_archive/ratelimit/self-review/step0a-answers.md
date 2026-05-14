# Step 0-A 自己採点シート

## 自力で出すべき `[QUESTION]` / `[AMBIGUITY]`

依頼書 `client-brief/2026-05-14_ratelimit.md` から **必ず引き出すべき** 問い。
書けていない項目があれば Step 0-A を未完了とみなし、Step 0-A をやり直す。

### 必須 `[QUESTION]`

- [ ] **Q1**: 上限値・窓幅 — 「何 req / 何秒で制限するか」
- [ ] **Q2**: 対象 API — 「全エンドポイントか、一部か」
- [ ] **Q3**: 超過時応答 — 「HTTP ステータスとボディは」
- [ ] **Q4**: レスポンスヘッダ — 「`Retry-After` / `X-RateLimit-*` は付けるか」
- [ ] **Q5**: 識別キー — 「ユーザー単位か IP 単位か」

### 必須 `[AMBIGUITY]`

- [ ] **A1**: 「特定の顧客から大量リクエスト」 → 顧客単位（user_id / API key） vs IP 単位
- [ ] **A2**: 「FastAPI のミドルウェアで」 → 全ルートに掛ける / 一部だけ

### 加点 `[QUESTION]`

- [ ] ストレージ: 既存 Memorystore を流用するか別インスタンスか
- [ ] 環境: 本番のみか dev / stg も含むか
- [ ] 監視: メトリクス・アラートを Phase に含むか
- [ ] IPv6 / プロキシチェーンの取り扱い

---

## 想定回答（自力で `[QUESTION]` を書き出してから読む）

`[QUESTION]` を全部書き出した後で `client-brief/2026-05-15_qa.md` を開く。
そこに想定回答が記載されている。要点だけ列挙すると:

| # | 回答 |
|---|---|
| Q1 | 60 req / 60s（固定窓） |
| Q2 | `/users` と `/orders` のみ。`/health` は除外 |
| Q3 | 429、ボディ `{"detail": "rate limit exceeded"}` |
| Q4 | `Retry-After` 必須、`X-RateLimit-Limit / Remaining / Reset` を成功時に付与 |
| Q5 | 認証済は user_id、未認証は X-Forwarded-For 先頭 IP |
| ストレージ | 既存 Memorystore 流用 |
| 環境 | 全環境 |
| 監視 | Non-Goal（別チケット） |

---

## NG パターン（自分の出力をこの基準でチェック）

- [ ] 「一般的には 100 req/min なので…」と `[ASSUMPTION]` 無しで決めていないか
- [ ] 対象 API を確認せず「全 API に適用」と勝手に決めていないか
- [ ] 「FastAPI ミドルウェアで」と書いてあるのに `slowapi` 等を勝手提案していないか
- [ ] What / Done / Constraints / Non-Goals が構造化されているか

3 つ以上抜けていたら Step 0-A をやり直し。
