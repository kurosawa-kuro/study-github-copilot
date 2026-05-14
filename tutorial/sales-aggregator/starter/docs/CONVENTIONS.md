# コーディング規約

## Python

- PEP 8（snake_case / PascalCase / UPPER_SNAKE_CASE）
- 型注釈必須、`from __future__ import annotations` を使う
- 例外は具象を捕捉、`except Exception` は禁止（テスト除く）
- `print` は CLI 出力以外で使わない（ログは構造化前提だが本教材スコープ外）

## CSV

- エンコーディング: **UTF-8**（BOM 無し）
- 区切り: **`,`**
- 改行コード: **LF**
- ヘッダ行あり

## Redis

- ローカルでは `docker compose up -d` で起動（[`../compose.yaml`](../compose.yaml)）
- 接続先: `redis://localhost:6379/0`
- キー命名: コロン区切り名前空間（例: `app:report:product:<id>`）
- **TTL と用途をコメントで明示**

## テスト

- pytest + **fakeredis**（testcontainers は採用しない）
- 全変更にテストコード必須
- 正常系 1 / 異常系 1 / 境界値は必要に応じて

## インフラ

- ローカル開発で Redis を立てる以外、クラウド・IaC は本教材スコープ外
- 機密は環境変数経由（ハードコード禁止）

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
