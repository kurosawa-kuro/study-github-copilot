# Step 0-C 自己採点シート

QUICK_GUIDE.md の Step 0-C プロンプトを貼った後、以下が確実に固定されているか確認する。

## 本チュートリアルで固定すべき値

- [ ] アプリ言語: Python 3.12
- [ ] フレームワーク: FastAPI
- [ ] Redis クライアント: redis-py
- [ ] テスト: pytest + **fakeredis**（testcontainers ではない）
- [ ] 依存管理: uv
- [ ] IaC: Terraform（**今回は変更しない**）
- [ ] Redis キー規約: `app:<feature>:<id>`
- [ ] 認証方式: Bearer トークン（既存 middleware）
- [ ] 後方互換性: **必須**（既存 `/users` / `/orders` / `/health` を壊さない）
- [ ] 出力ルール: `[ASSUMPTION]` / `[QUESTION]` / `[BREAKING]` 等のタグ付け必須

## 自分の出力でやってないか確認

- [ ] `slowapi` 等のサードパーティ採用を提案していないか
- [ ] testcontainers-redis を使い始めていないか
- [ ] Terraform 変更を Phase に含めていないか
- [ ] 監視・アラート設計を始めていないか

## 完了の合図

最後に「**前提固定完了**」が出力されているか確認。
