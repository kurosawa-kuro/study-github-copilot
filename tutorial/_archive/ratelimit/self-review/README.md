# 自学自習モード用 自己採点シート

ファシリ無しでチュートリアルを進める受講者向け。
各 Step の出力を自分で採点するための **チェックリストと想定回答** をまとめる。

## 使い方

1. QUICK_GUIDE.md のフロー順に進める（[../README.md](../README.md) のモード B 参照）
2. **各 Step を完了したら、対応するファイルを開いて自己採点**
3. チェック項目が満たせていないと感じたら、その Step に戻ってやり直し
4. `solution/` は **全工程が終わるまで開かない**（学習効果がゼロになる）

## ファイル

| ファイル | 役割 |
|---|---|
| `step0a-answers.md` | Step 0-A で出すべき `[QUESTION]` / `[AMBIGUITY]` 一覧と、クライアント想定回答 |
| `step0c-checklist.md` | Step 0-C 前提固定で押さえるべき値 |
| `step1-checklist.md` | Step 1 で発見すべき既存コード箇所と `[BREAKING]` 候補 |
| `step2-checklist.md` | Step 2 Phase 分割の合格ライン |
| `step3-4-loop-hints.md` | Step 3 → 4 で起きやすい戻り先判定のヒント（ネタバレ最小） |
| `step5a-checklist.md` | Step 5-A 統合検証の判定基準 |
| `final-rubric.md` | 最終的な総合評価（A/B/C 判定） |

## 自学自習モードのルール

- `solution/` は **全 Step 完了後** にしか開かない
- `client-brief/2026-05-15_qa.md`（拡張版・クライアント回答）は、`[QUESTION]` を **自力で全部書き出してから** 読む
- `facilitator-guide/` は ファシリ前提のドキュメント。読みたければ最後の振り返り時に
