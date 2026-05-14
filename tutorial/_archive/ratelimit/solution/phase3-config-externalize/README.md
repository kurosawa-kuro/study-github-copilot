# Phase 3: 設定外出し + ヘッダ整備

## 目的

Phase 2 でハードコードされていた `limit=60` / `window=60` / 対象 path を `RatelimitSettings` に逃がし、
環境変数 (`MYAPI_RATELIMIT__*`) で上書き可能にする。あわせて `X-RateLimit-Limit` /
`X-RateLimit-Remaining` / `X-RateLimit-Reset` ヘッダを成功応答にも付与する。

## 変更ファイル

| パス | 種別 | 概要 | 想定行数 | このディレクトリ内の成果物 |
|---|---|---|---|---|
| `src/myapi/core/config.py` | 変更 | `RatelimitSettings` を `Settings` の入れ子に追加 | 約 20 | `config.py` |
| `src/myapi/main.py` | 変更 | 設定からインスタンス生成、成功応答にもヘッダ付与 | 約 30 | `main.py` |
| `tests/conftest.py` | 変更 | `ratelimit_cfg` fixture を追加し `client` に渡す | 約 10 | `conftest.py` |
| `tests/test_ratelimit.py` | 変更 | ヘッダ検証 / 設定差し替え / path filter テストを追加 | 約 50 | `test_ratelimit.py` |
| `.env.example` | 新規 | 環境変数サンプル | 約 10 | `.env.example` |

## 公開インタフェース

```python
class RatelimitSettings(BaseModel):
    limit: int = 60
    window_seconds: int = 60
    target_path_prefixes: tuple[str, ...] = ("/users", "/orders")
    excluded_paths: frozenset[str] = frozenset({"/health", "/openapi.json", "/docs"})


def create_app(kv: RedisKV | None = None, cfg: RatelimitSettings | None = None) -> FastAPI: ...
```

## 完了条件

- 機能条件: `MYAPI_RATELIMIT__LIMIT=5` を環境変数で渡すと 6 回目で 429
- 機能条件: 成功応答に `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` が付く
- テスト条件: 全テストパス（`tests/test_ratelimit.py` のヘッダ・設定差し替えケース含む）
- 検証コマンド: `uv run pytest -q`
- 追加検証: `MYAPI_RATELIMIT__LIMIT=5 uv run pytest tests/test_ratelimit.py -q`

## ロールバック手順

- `Settings` から `ratelimit` フィールドを削除し、`main.py` を Phase 2 の `_LIMIT` / `_WINDOW_SECONDS` ハードコード版に戻す

## 注意 [OUT-OF-SCOPE]

- `X-RateLimit-*` ヘッダの命名を IETF draft-ietf-httpapi-ratelimit-headers に揃える件は別チケット
- ヘッダ衝突（gateway 側で別の `X-RateLimit-*` を吐く場合）は Step 5-A の E2E で観察

## 引き継ぎ JSON

`../handoff-jsons/phase3.json` を参照。
