# チュートリアル: API レートリミット導入（中規模 / 標準フロー）

QUICK_GUIDE.md の標準フロー `0-A → 0-C → 1 → 2 → [3→4]×N → 5-A` を 1〜2 日で一周する例題。

## 学べること

- Step 0-A の **要件明確化** で `[QUESTION]` / `[AMBIGUITY]` を発見する力
- 既存コードに対する Step 1 **影響範囲調査** と `[BREAKING]` 検出
- Step 2 の **Phase 分割**（1 Phase = 1 コミット / 300 行以内 / 完了条件3種）
- Step 3 → Step 4 ループでの **戻り先判定**
- Step 5-A での **累積副作用検査**

## 規模感

- 想定時間: 8〜12 時間（半日 × 2 / ハンズオン半日 + 復習半日）
- ペア／モブ推奨（Step 4 のレビューが深まる）

## 進め方

1. `client-brief/2026-05-14_ratelimit.md` を**先に読まず**、まず `starter/` の構造を眺める
2. `client-brief/` を読み、QUICK_GUIDE.md の Step 0-A プロンプトを Copilot に貼って構造化
3. 以降は QUICK_GUIDE.md のフロー順に進行
4. 各 Phase の Step 4 完了時に **引き継ぎ JSON** を `handoff/phase{N}.json` に保存
5. 詰まったらファシリが `facilitator-guide/` を見ながら誘導

## ディレクトリ

| パス | 役割 |
|---|---|
| `client-brief/` | クライアントから届いた依頼書（意図的に薄い） |
| `starter/` | 受講者が修正していくベースコード |
| `solution/` | 模範解答（Phase ごと）と引き継ぎ JSON 見本 |
| `facilitator-guide/` | ファシリテーター用ガイド・期待アウトプット・ルーブリック |

## 評価

`facilitator-guide/99-rubric.md` を参照。

- **A**: 全 Step 通過 / タグ運用妥当 / 戻り先判定1回以上発生して対処
- **B**: 完了するが `[QUESTION]` が浅い／タグ無し推測が混入
- **C**: Step 0-A をスキップ／Phase 分割無し
