# チュートリアル: 日次売上の累積レポート

QUICK_GUIDE.md の標準フロー `0-A → 0-C → 1 → 2 → [3→4]×N → 5-A` を 1 日で一周する例題。
スタック: **Python / Docker / CSV / Redis**。API・クラウドは扱わない。

## 学べること

- Step 0-A の **要件明確化** で `[QUESTION]` / `[AMBIGUITY]` を発見する力
- 既存コードに対する Step 1 **影響範囲調査** と `[BREAKING]` 検出
- Step 2 の **Phase 分割**（1 Phase = 1 コミット / 完了条件 3 種）
- Step 3 → Step 4 ループでの **戻り先判定**
- Step 5-A での **E2E 検証**（特に冪等性の確認）

## 規模感

- 想定時間: 4〜8 時間
- Phase は 3 つに分割（Redis 抽出 → 累積マージ → 冪等性）

## 進め方

1. `client-brief/request.md` を読む（意図的に薄い依頼書）
2. QUICK_GUIDE.md の Step 0-A プロンプトを Copilot に貼り、`[QUESTION]` を全部書き出す
3. 以降は QUICK_GUIDE.md のフロー順に進める
4. 各 Phase の Step 4 完了時、引き継ぎ JSON を出して次 Phase へ
5. Step 5-A で `e2e/scenarios.sh` を実行し、結果を引き継ぎに貼る

詰まったら `solution/` を見る前に、依頼書と CONVENTIONS を読み返す。

## ディレクトリ

| パス | 役割 |
|---|---|
| `client-brief/request.md` | クライアントから届いた依頼書（意図的に薄い） |
| `starter/` | 受講者が修正していくベースコード |
| `solution/` | 模範解答（Phase ごとの完全成果物） |
| `e2e/` | Step 5-A 統合検証用ハーネス（`compose.yaml` + `scenarios.sh`） |

## 想定される `[QUESTION]`（Step 0-A）

依頼書から、最低限以下は引き出されるべき:

- 累積の単位（商品 ID のみ？日別？月別？カテゴリ？）
- 同じファイルを 2 回投入したらどうなる？（idempotency）
- Redis 上の累積データのリセット条件・保持期間
- 金額の型（円・整数？小数？通貨複数？）
- CSV のスキーマ（列順・エンコーディング・区切り・ヘッダ有無）
- 異常データ（負の数量など）への扱い
