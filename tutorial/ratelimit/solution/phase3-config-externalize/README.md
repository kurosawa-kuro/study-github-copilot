# Phase 3: 設定外出し + ヘッダ整備

## 目的

ハードコードされていた `limit=60` / `window=60` / 対象 path を `Settings` に逃がし、
`X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` ヘッダを成功応答にも付与。

## 変更ファイル

| パス | 種別 | 概要 | 想定行数 |
|---|---|---|---|
| `src/myapi/core/config.py` | 変更 | `RatelimitSettings` を `Settings` に追加 | 約 20 |
| `src/myapi/main.py` | 変更 | 設定からインスタンス生成、レスポンスヘッダ付与 | 約 20 |
| `tests/test_ratelimit.py` | 変更 | ヘッダアサーション追加 | 約 30 |
| `.env.example` | 新規 | 環境変数サンプル | 約 10 |

## 公開インタフェース

```python
class RatelimitSettings(BaseModel):
    limit: int = 60
    window_seconds: int = 60
    target_path_prefixes: tuple[str, ...] = ("/users", "/orders")
    excluded_paths: frozenset[str] = frozenset({"/health", "/openapi.json", "/docs"})
```

## 完了条件

- 機能条件: 環境変数 `MYAPI_RATELIMIT_LIMIT=5` を渡すと 6 回目で 429
- 機能条件: 成功時に `X-RateLimit-Remaining` ヘッダが付く
- テスト条件: 全テストパス
- 検証コマンド: `MYAPI_RATELIMIT_LIMIT=5 uv run pytest tests/test_ratelimit.py -q`

## ロールバック手順

- `Settings` の `ratelimit` フィールドを戻し、`main.py` で旧定数を再設定

## 引き継ぎ JSON

`../handoff-jsons/phase3.json` を参照。
