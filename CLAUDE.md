# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリの性質

これは **「GitHub Copilot 用プロンプトテンプレート（v3 体系）」とそれを練習するハンズオン教材** のリポジトリ。アプリケーション本体ではなくドキュメント／教材が主成果物。日本語で運用されている。

**目的**: Copilot の使い方を学ぶこと。クラウド技術・特定フレームワークを学ぶことではない。

**学習スコープ**: `Python / Docker / CSV / Redis`。これ以外（API / Web / クラウド固有サービス / IaC）は **意図的にスコープ外**。

主成果物は 2 種類:

1. `docs/QUICK_GUIDE.md` / `docs/PROMPT_TEMPLATE.md` — 案件で Copilot に貼り付けるプロンプトテンプレ。**QUICK_GUIDE が Step 本文の単一正本（実運用で貼る・規模別フロー・タグ・戻り先判定表を含む）、PROMPT_TEMPLATE は設計仕様（体系の根拠・運用上の留意点・段階導入ガイド・領域別適用差・改訂履歴）**。PROMPT_TEMPLATE は Step 本文を持たず QUICK_GUIDE を参照する形に整理されている。両者の役割分担を壊さないこと。
2. `tutorial/` — 新題材を準備中。過去版（`tutorial/_archive/ratelimit/` = FastAPI + Redis）は題材ミスマッチのため退避済み、参照不要。

## 体系の中核概念（編集時に壊してはいけないもの）

- **規模別フロー**: 案件規模で実行する Step の組み合わせが決まる（小規模 `0-C→1→3→4` / 標準 `0-A→0-C→1→2→[3→4]×N→5-A` / 大規模 `+5-B`）。フローを変える編集は体系全体に波及する。
- **タグ運用**: `[ASSUMPTION]` `[QUESTION]` `[AMBIGUITY]` `[OUT-OF-SCOPE]` `[BREAKING]` `[BLOCKER]`。**タグなしの推測・決定は不完全とみなして差し戻し**、というルールがリポジトリ全体の前提。生成物に推測を入れるときは必ずタグを付ける。
- **戻り先判定（Step 4 → 戻る先）**: 軽微なバグ→3 / 完了条件不備→2 / 既存矛盾→1 / 設計欠陥→0-B / 要件曖昧→0-A。Step 4 の出力が「次にどこへ戻るか」を含むのが v3 の本質。
- **Phase 分割の規約**: 1 Phase = 1 コミット / 300 行以内 / 完了条件 3 種（検証コマンド必須）/ Phase 間引き継ぎ JSON。これは Step 2 の不可侵な制約。
- **テストコード必須**: 全変更にテストコードが付くこと。テスト無しのコード変更は不完全とみなす。

## 新題材を作るときのルール

`tutorial/` 配下に新規教材を作るとき:

- 題材は **Python / Docker / CSV / Redis** で完結すること。API / Web / クラウド固有サービスは入れない
- 動線は **一本**（モード A/B 併存などの複雑な仕様を作らない）
- ディレクトリ構成: `client-brief/` / `starter/` / `solution/` / `e2e/`（必要なら）
- starter は `uv sync --extra dev` → `uv run pytest -q` が緑であることが前提
- Redis を使うテストは **fakeredis**、Redis 起動は **Docker compose**
- 全変更にテストコード必須

`_archive/ratelimit/` の内部構造（self-review / facilitator-guide / S/A/B/C ルーブリック）は **過剰**。新題材では踏襲しない。

## ドキュメント編集時の注意

各情報の **単一正本** を以下に固定する。重複コピーを増やさず、参照リンクで誘導すること。

| 情報 | 単一正本 | 他ファイルでは |
|---|---|---|
| Step 0-A〜5-C のプロンプト本文 | `docs/QUICK_GUIDE.md` | 参照リンクのみ |
| 規模別フロー早見表 | `docs/QUICK_GUIDE.md` | 参照リンクのみ |
| タグ一覧 | `docs/QUICK_GUIDE.md` | 参照リンクのみ |
| 戻り先判定表 | `docs/QUICK_GUIDE.md` | 参照リンクのみ |
| 工程全体マップ・ループ図 | `docs/PROMPT_TEMPLATE.md` | 簡易図のみ可 |
| 段階導入ガイド / 領域別適用差 | `docs/PROMPT_TEMPLATE.md` | 参照リンクのみ |
| 運用上の留意点（破綻条件） | `docs/PROMPT_TEMPLATE.md` | 参照リンクのみ |
| 改訂履歴 | `docs/PROMPT_TEMPLATE.md` | 参照リンクのみ |

- 改訂順序: PROMPT_TEMPLATE → QUICK_GUIDE → README → CLAUDE → tutorial の順で更新する
- Step 0-B（設計判断）と Step 5-C（振り返り）は **意図的に「保留」状態**。「必要が出てから整備」という段階導入方針のため、勝手に中身を埋めない
- スタック制約は **二重スコープ** で管理する:
  - `docs/QUICK_GUIDE.md` / `docs/PROMPT_TEMPLATE.md`（テンプレ本体）: **特別例外**。実案件想定で `Python / Docker / Redis / GCP / Terraform` を汎用スタックとして例示してよい
  - `tutorial/` 配下（教材）: 狭く `Python / Docker / CSV / Redis` のみ。API / Web / クラウド固有サービスは入れない
- 教材のスコープ違反（API / Web / クラウド固有名）を tutorial に持ち込まないこと
