# Step 1 自己採点シート

## 既存コードで発見すべき箇所

`starter/src/myapi/` を grep で読み、以下を **ファイルパスと行番号付きで列挙** したか確認:

- [ ] `core/redis_client.py` — `UserCacheRedis` が User 専用に密結合（汎用 KV を抽出する必要）
- [ ] `routers/orders.py` — コメントに「gateway 側 600 req/min」**`[BREAKING]` 候補**
- [ ] `routers/health.py` — `/health` の存在（middleware で除外する根拠）
- [ ] `main.py` — 既存 auth middleware の存在と順序（middleware 順序の論点）
- [ ] `core/config.py` — Pydantic Settings 経由が既存規約（Phase 3 への伏線）

## 実現可否

- [ ] **△**（実現可能だが要設計判断あり）と判定したか
- [ ] 影響範囲を「直接変更」「間接影響」「未影響」の 3 層で分類したか
- [ ] 代替案を最低 2 つ提示し、トレードオフ比較したか
  - 候補 A: 固定窓 `INCR + EXPIRE`（シンプル）
  - 候補 B: スライディングウィンドウ（Lua）（精度高・複雑）
  - 候補 C: トークンバケット（状態複雑）

## 必須で挙げるべき `[BREAKING]`

- [ ] `/orders` のゲートウェイ側 600 req/min と二重制御になる件
- [ ] ヘッダ衝突（`X-RateLimit-*`）の有無

**これが出ていなければ Step 1 未完了。Step 1 をやり直し。**

## NG パターンチェック

- [ ] 既存コードを引用せず「実装可能です」と一般論で回答していないか
- [ ] 影響範囲の 3 層分類が無いまま結論を出していないか
- [ ] 代替案が 1 つしかない
