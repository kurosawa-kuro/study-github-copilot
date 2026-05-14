# Step 5-A 自己採点シート

## 入力の準備

- [ ] Phase 1〜3 の引き継ぎ JSON 3 つを時系列で並べた

## Phase 間整合性

- [ ] Phase 1 `deferred_items`（コネクションプール）が Phase 2 で実害なく済んだか
- [ ] Phase 2 `deferred_items`（設定外出し・ヘッダ整備）が Phase 3 で全消化されているか
- [ ] Phase 2 `breaking_changes`（gateway 二重制御）に対する **判断** が明示されているか

## E2E 動作

[../e2e/scenarios.sh](../e2e/scenarios.sh) を実行し、出力を引き継ぎに貼る:

- [ ] シナリオ 1〜6 全部 OK
- [ ] 失敗があれば該当 Phase に差し戻し（戻り先明記）

## 累積副作用

- [ ] `redis_client.py` の旧 API 残骸が無い（`UserCacheRedis` の外部 API は不変）
- [ ] `pytest` 全体の所要時間が極端に増えていない
- [ ] middleware で毎リクエスト print していない（ログ過多回避）

## 残存 `[OUT-OF-SCOPE]` 棚卸し

- [ ] ヘッダ命名の IETF 準拠 → 別チケット候補
- [ ] 監視・アラート → 別チケット必須
- [ ] スライディングウィンドウへの将来切替 → 保留

すべて ◯ なら「**統合完了**」を出力。
× が一つでもあれば該当 Phase に差し戻し。
