# 03. Step 1 実現可能性調査 — 仕込みと罠

## 受講者が grep で見つけるべき既存コード

| ファイル | 何を発見すべきか | タグ |
|---|---|---|
| `src/myapi/core/redis_client.py` | `UserCacheRedis` が User 専用に密結合 → 汎用 KV 抽出が必要 | 設計上の課題 |
| `src/myapi/routers/orders.py` | コメントに「gateway 側 600 req/min」と記載 | **`[BREAKING]` 候補** |
| `src/myapi/routers/health.py` | `/health` の存在 → middleware で除外する根拠 | 仕様確認 |
| `src/myapi/main.py` | 既存 auth middleware の存在と順序 | middleware 順序の論点 |
| `src/myapi/core/config.py` | Pydantic Settings 経由が既存規約 | Phase 3 への伏線 |

## 期待される実現可否

- **△**（実現可能だが要設計判断あり）
- 推奨案: 「汎用 KV を先に抽出 → middleware → 設定外出し」の3 Phase
- 代替案として挙がるべきもの:
  - **A**: スライディングウィンドウ（Lua スクリプト）→ 精度高いが複雑、Non-Goal
  - **B**: 固定窓 `INCR + EXPIRE` → シンプル、本案
  - **C**: トークンバケット → メモリ効率良いが状態複雑

## 必須で挙がるべき `[BREAKING]`

> `/orders` はゲートウェイ側で 600 req/min の制限が既にある。新規 60 req/min と二重制御になる。
> ヘッダ衝突（`X-RateLimit-*`）の有無も Phase 2 で要確認。

これが Step 1 の出力に含まれていなければ **未完了**。差し戻し。

## 必須で挙がるべき `[QUESTION]`

- middleware 登録順序（auth 前か後か）
- IPv6 / プロキシチェーンの取り扱い（Phase 2 仕込みでも可）

## NG パターン

- 既存コードを引用せずに「実装可能です」と回答 ← 一般論回答、差し戻し
- 影響範囲を「直接変更 / 間接影響 / 未影響」の 3 層で分類していない
- 代替案を 1 つしか出さない（QUICK_GUIDE.md は最低2つを要求）
