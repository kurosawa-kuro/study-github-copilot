# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリの性質

これは **「GitHub Copilot 用プロンプトテンプレート（v3 体系）」とそれを練習するハンズオン教材** のリポジトリ。アプリケーション本体ではなくドキュメント／教材が主成果物。日本語で運用されている。

主成果物は 2 種類:

1. `docs/QUICK_GUIDE.md` / `docs/PROMPT_TEMPLATE.md` — 案件で Copilot に貼り付けるプロンプトテンプレ。**QUICK_GUIDE が Step 本文の単一正本（実運用で貼る・規模別フロー・タグ・戻り先判定表を含む）、PROMPT_TEMPLATE は設計仕様（体系の根拠・運用上の留意点・段階導入ガイド・領域別適用差・改訂履歴）**。PROMPT_TEMPLATE は Step 本文を持たず QUICK_GUIDE を参照する形に整理されている。両者の役割分担を壊さないこと。
2. `tutorial/ratelimit/` — そのテンプレを使って一周する中規模ハンズオン（FastAPI + Redis のレートリミット導入）。`starter/` / `solution/` / `client-brief/` / `facilitator-guide/` の 4 つで構成され、それぞれ役割が分離している（後述）。

## 体系の中核概念（編集時に壊してはいけないもの）

- **規模別フロー**: 案件規模で実行する Step の組み合わせが決まる（小規模 `0-C→1→3→4` / 標準 `0-A→0-C→1→2→[3→4]×N→5-A` / 大規模 `+5-B` / インフラ `0-C→1→2→[3→4]×N→5-B`）。フローを変える編集は体系全体に波及する。
- **タグ運用**: `[ASSUMPTION]` `[QUESTION]` `[AMBIGUITY]` `[OUT-OF-SCOPE]` `[BREAKING]` `[BLOCKER]`。**タグなしの推測・決定は不完全とみなして差し戻し**、というルールがリポジトリ全体の前提。生成物に推測を入れるときは必ずタグを付ける。
- **戻り先判定（Step 4 → 戻る先）**: 軽微なバグ→3 / 完了条件不備→2 / 既存矛盾→1 / 設計欠陥→0-B / 要件曖昧→0-A。Step 4 の出力が「次にどこへ戻るか」を含むのが v3 の本質。
- **Phase 分割の規約**: 1 Phase = 1 コミット / 300 行以内 / 完了条件 3 種（検証コマンド必須）/ Phase 間引き継ぎ JSON。これは Step 2 の不可侵な制約。

## ハンズオン (`tutorial/ratelimit/`) の役割分離

ファイルを編集する前にどのディレクトリに属するか必ず確認する:

| ディレクトリ | 役割 | 編集時の注意 |
|---|---|---|
| `client-brief/` | クライアントから届いた「意図的に薄い」依頼書 | 受講者が `[QUESTION]` を引き出すための練習素材。**薄さは意図的なので、勝手に補完しない** |
| `starter/` | 受講者が修正していくベースコード | 既存テストが全パスする状態を維持。`uv sync --extra dev` → `uv run pytest -q` がグリーンであることが教材の前提 |
| `solution/` | 模範解答（Phase 1〜3 のディレクトリ + `handoff-jsons/`） | **受講者は見ない**。ファシリ専用。Phase 1=Redis 抽象化 / 2=middleware / 3=設定外出し の順序は固定 |
| `facilitator-guide/` | ファシリ用ガイド・期待される `[QUESTION]` 一覧・ルーブリック | ファシリの設計判断介入を抑止する立て付け。`99-rubric.md` が評価基準の正本 |

## starter プロジェクトのコマンド

`tutorial/ratelimit/starter/` 内で実行:

```bash
uv sync --extra dev                              # 依存セットアップ（dev extras 含む）
uv run pytest -q                                 # 全テスト
uv run pytest tests/test_users.py::test_xxx     # 単一テスト
uv run uvicorn myapi.main:app --reload          # ローカル起動
uv run ruff check src tests                      # lint
uv run mypy src                                  # 型チェック（strict）
```

- Python 3.12 必須。依存管理は **uv** 前提（pip でも動くが README は uv で書かれている）。
- Redis を使うテストは **fakeredis** で書く（testcontainers は採用しない、という明示的な決定）。
- `terraform/` ディレクトリは **チュートリアル内では変更しない前提**（Memorystore + Cloud Run の参考構成として置いてある）。

## starter のコーディング規約（`tutorial/ratelimit/starter/docs/CONVENTIONS.md` が正本）

- 型注釈必須、`from __future__ import annotations` 使用。
- `except Exception` 禁止（テスト除く）。例外は具象を捕捉。
- `print` 禁止（構造化ログ前提、ただし本チュートリアルのスコープ外）。
- Redis キーは `app:<feature>:<id>` のコロン区切り名前空間。**用途と TTL をコメントで明示**。例: `app:user:<user_id>` (TTL 60s)。
- 環境変数は `MYAPI_` プレフィックス。機密は Secret Manager 経由（ハードコード禁止）。

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
