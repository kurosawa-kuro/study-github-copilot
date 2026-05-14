# 05. Step 3 → Step 4 ループ — 意図的に起こす戻り先判定

## Phase 1（Redis 抽象化）

- ほぼストレートに完了する想定
- Step 4 で見るべき: 既存テストが**全パスしているか**（後方互換性チェック）
- 引き継ぎ JSON で `breaking_changes: []` であること

### 起こりがちな小ミス

- `UserCacheRedis.__init__` のシグネチャ変更（旧引数 `client` を `kv` に置き換えた場合の呼び出し元）
  → 軽微なバグ → **戻り先: Step 3**

---

## Phase 2（middleware 実装）★ 戻り先判定が起きやすい

### 期待される問題（ファシリが見抜く）

| 症状 | 戻り先 | 修正 |
|---|---|---|
| `/health` がレートリミット対象になっている | Step 3（実装漏れ） | 除外パスを判定に追加 |
| middleware が auth より先に走り、未認証リクエストで user_id が無い前提が壊れる | Step 2（完了条件で順序未指定） | Step 2 で順序を完了条件に追加してから Step 3 やり直し |
| `INCR` の初回 EXPIRE タイミングが race condition | Step 3 | 初回 (return == 1) のみ EXPIRE する |
| `[BREAKING]` 検出していない（`/orders` の gateway 既存制限） | Step 1 | Step 1 まで戻って影響範囲調査やり直し |
| 429 に `Retry-After` が無い | Step 3 | レスポンスヘッダ追加 |

### 戻り先判定 模範例

> Phase 2 レビュー結果:
> - 観点1 完了条件: × — middleware 順序が完了条件に含まれていなかった
> - **戻り先: Step 2**（完了条件不備）
> - 修正案: Step 2 の Phase 2 完了条件に「auth middleware より後で評価されること」を追加し、
>   Step 3 で `@app.middleware("http")` 登録順を保証するテストを追加

### 引き継ぎ JSON で必須

- `breaking_changes` に `/orders` ゲートウェイ二重制御の件が入っている
- `assumptions_made` に X-Forwarded-For 信頼の `[ASSUMPTION]` が入っている

---

## Phase 3（設定外出し）

- ストレートに完了しやすい
- Step 4 で見るべき: 環境変数を変えてテストが通るか実演
- ヘッダ命名（`X-RateLimit-*`）は IETF draft 準拠を `[OUT-OF-SCOPE]` で挙げる

---

## ファシリが意図的に介入するタイミング

1. **Phase 2 で受講者が完了条件をふわっと書いた場合** → そのまま Step 3 に進ませる
   → 実装後に middleware 順序問題が顕在化 → **Step 2 戻りを体験させる**
2. **Phase 1 で gateway 既存制限を見落とした場合** → そのまま進ませる
   → Phase 2 Step 4 で発覚 → **Step 1 戻りを体験させる**

「戻り先判定が一度も発生しない」進行は学習効果が薄い。
**最低 1 回は戻り先判定を起こさせる**。
