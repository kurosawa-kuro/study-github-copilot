# コーディング規約

## Python

- PEP 8（snake_case / PascalCase / UPPER_SNAKE_CASE）
- 型注釈は必須、`from __future__ import annotations` を使う
- 例外は具象を捕捉、`except Exception` は禁止（テスト除く）
- ログは構造化ログ前提（今回のスコープでは print 禁止）

## Redis キー

- **コロン区切り名前空間**: `app:<feature>:<id>`
- 用途と TTL をコメントで明示
- 例: `app:user:<user_id>` (TTL 60s, User キャッシュ用)

## テスト

- pytest 採用、fixture は `tests/conftest.py` に集約
- Redis を使うテストは **fakeredis** で書く（testcontainers は採用しない）
- 正常系1つ・異常系1つ・境界値は必要に応じて

## タグ運用（QUICK_GUIDE.md 由来）

| タグ | 用途 |
|---|---|
| `[ASSUMPTION]` | 推測で埋めた箇所 |
| `[QUESTION]` | 確認事項 |
| `[AMBIGUITY]` | 解釈の分岐がある |
| `[OUT-OF-SCOPE]` | 範囲外 |
| `[BREAKING]` | 既存に反する |
| `[BLOCKER]` | デプロイ阻害 |

タグ無しの推測・決定はレビューで差し戻し対象。

## IaC

- 手動変更禁止（コンソールから触らない）
- remote backend (GCS) 必須
- 本チュートリアルでは `terraform/` は**変更しない**前提

## セキュリティ

- 機密は Secret Manager 経由、ハードコード禁止
- 環境変数は `MYAPI_` プレフィックス
