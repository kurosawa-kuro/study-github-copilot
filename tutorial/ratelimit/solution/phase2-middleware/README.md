# Phase 2: レートリミット middleware 実装

## 目的

固定窓 (60s) で `INCR + EXPIRE` パターンの API レートリミット middleware を実装。
識別キーは「認証済 → user_id / 未認証 → X-Forwarded-For 先頭 IP」。
対象は `/users`, `/orders`。`/health` は除外。超過時 429 + `Retry-After`。

## 変更ファイル

| パス | 種別 | 概要 | 想定行数 |
|---|---|---|---|
| `src/myapi/core/ratelimit.py` | 新規 | `RateLimiter` クラス、固定窓ロジック | 約 80 |
| `src/myapi/main.py` | 変更 | middleware 登録（auth より後ろ）、`/health` 除外 | 約 30 |
| `tests/test_ratelimit.py` | 新規 | 上限内 / 超過 / 窓リセット / `/health` 除外 / IP fallback | 約 120 |

## 公開インタフェース

```python
class RateLimiter:
    def __init__(self, kv: RedisKV, limit: int, window_seconds: int) -> None: ...
    def check(self, identifier: str) -> RateLimitResult: ...

@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_in_seconds: int
```

## 完了条件

- 機能条件: `/users/{id}` を同一識別子で 61 回叩くと 61 回目が 429。`/health` は何回叩いても 200
- テスト条件: `tests/test_ratelimit.py` 全パス、既存テスト全パス
- 検証コマンド: `uv run pytest -q`
- ヘッダ要件: 429 時に `Retry-After` 必須

## ロールバック手順

- `app.middleware("http")` の登録を削除（auth より後の1ブロック）

## 注意 [BREAKING] 検出

Step 1 で発見されているはずの **`/orders` ゲートウェイ側 600 req/min** との二重制御に注意。
本 Phase の上限値 60/min はゲートウェイより厳しいため挙動として支配的になる。
gateway 側で先に絞られるケースは無いが、`X-RateLimit-*` ヘッダ衝突は要確認 → Phase 3 で整える。

## 引き継ぎ JSON

`../handoff-jsons/phase2.json` を参照。
