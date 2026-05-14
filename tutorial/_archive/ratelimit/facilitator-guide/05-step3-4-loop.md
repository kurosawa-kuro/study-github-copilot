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

---

## 難難度シナリオ（自発的発見で +1）

仕掛けで誘発する戻り判定（middleware 順序 / gateway 二重制御）は **易〜中** 難度。
受講者が **自分で気づいて** 戻り先判定を発生させると **S 評価相当**。

| 症状 / 観点 | 戻り先 | 期待される受講者の発言 |
|---|---|---|
| `X-RateLimit-Reset` の単位曖昧（epoch 秒 / 残秒 / RFC 3339） | Step 0-A | 「依頼書に Reset 単位の指定が無い。確認します」 |
| Phase 2 で `INCR + EXPIRE` の race で初回数件が TTL なしで残る可能性 | Step 1 → Step 2 | 「Lua スクリプト化 or `SET NX EX` パターンを検討」 |
| 識別子が `user_id` のとき、JWT 失効や user 削除後の **削除残骸** | Step 0-B | 「TTL に依存するが、Key 数の上限監視が要る」 |
| 認証なしフォールバック `X-Forwarded-For` 先頭の信頼境界 | Step 0-A | 「ゲートウェイ手前で偽装可能か `[QUESTION]`」 |
| `pytest` 並列実行時に fakeredis インスタンスが共有されると別テストが汚染 | Step 2 | 「conftest の `fake_redis` を function スコープで隔離」 |

これらは Step 4 のレビューで「自分で」`[BREAKING]` `[ASSUMPTION]` `[QUESTION]` のいずれかを発生させ、
戻り先を明示できれば加点。ファシリは聞かれない限り誘導しない。

---

## ファシリが「予防」を見抜く方法

Step 2 の作業計画書 の段階で、以下が含まれていれば「予防」とみなす:

- middleware 登録順序が Phase 2 完了条件に **明文で書かれている**
- `INCR + EXPIRE` の race を `[ASSUMPTION]` として明記 or Lua 化を `[OUT-OF-SCOPE]` で挙げている
- gateway 二重制御が Step 1 で `[BREAKING]` 検出済みで、Phase 2 計画に「衝突確認」が含まれる

予防に成功した受講者には、難難度の別シナリオ（上表）を `[QUESTION]` 形式で投げて Step 0-A 戻り体験を提供すると S 評価に持っていける。
