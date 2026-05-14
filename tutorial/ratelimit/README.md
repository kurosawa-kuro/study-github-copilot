# チュートリアル: API レートリミット導入（中規模 / 標準フロー）

QUICK_GUIDE.md の標準フロー `0-A → 0-C → 1 → 2 → [3→4]×N → 5-A` を 1〜2 日で一周する例題。

## 学べること

- Step 0-A の **要件明確化** で `[QUESTION]` / `[AMBIGUITY]` を発見する力
- 既存コードに対する Step 1 **影響範囲調査** と `[BREAKING]` 検出
- Step 2 の **Phase 分割**（1 Phase = 1 コミット / 300 行以内 / 完了条件 3 種）
- Step 3 → Step 4 ループでの **戻り先判定**
- Step 5-A での **累積副作用検査** と E2E

## 規模感

- 想定時間: 8〜12 時間（半日 × 2 / ハンズオン半日 + 復習半日）

---

## 運用モード

このチュートリアルは 2 つのモードで実行できる。

### モード A: ファシリ運用（推奨・ペア / モブ）

- ファシリが各 Step の `[QUESTION]` 想定回答を返しながら進行
- 戻り先判定の仕掛けを意図的に体験させる
- 進め方:
  1. `client-brief/2026-05-14_ratelimit.md`（薄い依頼書）だけを受講者に渡す
  2. 受講者が QUICK_GUIDE.md の Step 0-A プロンプトを Copilot に貼る
  3. ファシリは `facilitator-guide/01-step0a-expected-questions.md` を見ながら受講者の `[QUESTION]` をチェック・想定回答を返す
  4. 以降は QUICK_GUIDE.md のフロー順に進行、ファシリは各 Step の facilitator-guide を参照
  5. 評価: `facilitator-guide/99-rubric.md`

### モード B: 自学自習

- ファシリ無しで一人で進める
- 拡張版 client-brief（Q&A 形式）と自己採点シートを使う
- 進め方:
  1. `client-brief/2026-05-14_ratelimit.md` を読む（薄い依頼書）
  2. QUICK_GUIDE.md の Step 0-A プロンプトで `[QUESTION]` を自力で全部書き出す
  3. **書き終わってから** `client-brief/2026-05-15_qa.md`（クライアント回答）を開く
  4. `self-review/step0a-answers.md` で自己採点
  5. 以降の Step も `self-review/` の各シートで自己採点しながら進む
  6. 全部終わったら `solution/` と比較、`self-review/final-rubric.md` で総合評価
  7. ふりかえりを `retrospective/` に書いて保存（任意）

**自学自習モード重要ルール**:

- `solution/` は **全 Step 完了後** にしか開かない
- `client-brief/2026-05-15_qa.md` は `[QUESTION]` を自力で全部書き出してから開く
- 詰まったら `self-review/step3-4-loop-hints.md` をレベル別に開く

---

## ディレクトリ

| パス | 役割 |
|---|---|
| `client-brief/` | クライアントから届いた依頼書。薄い版 (`2026-05-14`) と Q&A 拡張版 (`2026-05-15`) |
| `starter/` | 受講者が修正していくベースコード |
| `solution/` | 模範解答（Phase ごとの完全成果物） |
| `facilitator-guide/` | **モード A 専用** ファシリガイド・期待アウトプット・ルーブリック |
| `self-review/` | **モード B 専用** 自己採点シート集 |
| `e2e/` | Step 5-A 統合検証用 E2E ハーネス（`compose.yaml` + `scenarios.sh`） |
| `retrospective/` | ふりかえりの蓄積場所（任意） |

## 評価

- モード A: `facilitator-guide/99-rubric.md`
- モード B: `self-review/final-rubric.md`

両モードとも、戻り先判定の **予防 / 発見** を A 級以上の必要条件として扱う。
