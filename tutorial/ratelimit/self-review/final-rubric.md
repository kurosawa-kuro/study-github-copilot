# 最終自己採点ルーブリック

自学自習版のため、戻り先判定の「予防 / 発見」を上位とする評価軸。

## 総合評価

| 評定 | 条件 |
|---|---|
| **S** | 仕掛けに気づいて Step 2 で **予防** ＋ 全 Step 通過 ＋ E2E 全シナリオ pass |
| **A** | Phase 2 等で戻り先判定が発生し、**自力で正しい戻り先を特定** ＋ 全 Step 通過 |
| **B** | 戻り先判定なしで完走（仕掛けに引っかからず、かつ予防もなし）または `[QUESTION]` が浅い |
| **C** | Step 0-A スキップ / Phase 分割なし / 検証コマンド実行結果なし / `[BREAKING]` 見落とし |

## Step 別自己採点（自分の出力にチェック）

各 Step のチェックリストに従って自己採点:

| Step | 採点シート |
|---|---|
| 0-A | [step0a-answers.md](step0a-answers.md) |
| 0-C | [step0c-checklist.md](step0c-checklist.md) |
| 1 | [step1-checklist.md](step1-checklist.md) |
| 2 | [step2-checklist.md](step2-checklist.md) |
| 3 / 4 | [step3-4-loop-hints.md](step3-4-loop-hints.md) |
| 5-A | [step5a-checklist.md](step5a-checklist.md) |

## 失格条件

- [ ] `solution/` を完了前に開いた
- [ ] タグ無しの推測を 3 件以上含む
- [ ] 既存 `/users` / `/health` テストを壊したまま完了宣言した

## 自己ふりかえり（書いて残す）

完了したら、以下を `retrospective/[氏名]_[日付].md` に書いて保存。

1. 一番効いた Step はどれか？ なぜ？
2. 戻り先判定が発生したのは Phase いくつ？ どの戻り先だった？
3. 予防できた仕掛けはあったか？
4. 依頼書の薄さに対して、何個の `[QUESTION]` を返したか？
5. `solution/` 通りでなかった判断と、その根拠
