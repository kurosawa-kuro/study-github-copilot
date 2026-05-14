# myapi (starter)

社内向け FastAPI サービス。ユーザー情報と注文を返す。

## 構成

- Python 3.12 / FastAPI / redis-py / pytest / fakeredis
- 依存管理: `pyproject.toml`（uv 想定）
- Redis: 用途は **ユーザーキャッシュ**（`core/redis_client.py`）
- インフラ: `terraform/envs/dev/` に Memorystore + Cloud Run（**今回は触らない**）

## 既知のメモ

- 認証は `routers/` の依存関数 `require_user` を通る（auth middleware は別途定義済み）
- `/orders` はゲートウェイ側で別途レート制御が入っている。詳細は `routers/orders.py` のコメント参照
- ヘルスチェックは `/health`（k8s liveness）

## 開発

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn myapi.main:app --reload
```

## 規約

`docs/CONVENTIONS.md` を必ず読むこと。Redis キー命名・タグ運用・テスト方針が記載されている。
