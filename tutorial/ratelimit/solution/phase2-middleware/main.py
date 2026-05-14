"""Phase 2 完了時の main.py 全体像.

固定窓レートリミット middleware を auth middleware と組み合わせて登録する。
limit / window / 対象 path はハードコード（Phase 3 で環境変数化）。
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from myapi.core.ratelimit import RateLimiter
from myapi.core.redis_kv import RedisKV, RedisKVImpl
from myapi.routers import health, orders, users

_EXCLUDED_PATHS = {"/health", "/openapi.json", "/docs"}
_RATELIMITED_PREFIXES = ("/users", "/orders")
_LIMIT = 60
_WINDOW_SECONDS = 60


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _auth_middleware_factory(app: FastAPI) -> None:
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        if request.url.path in _EXCLUDED_PATHS:
            return await call_next(request)
        auth = request.headers.get("authorization")
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "unauthorized"})
        request.state.user_id = auth.removeprefix("Bearer ").strip()
        return await call_next(request)


def _ratelimit_middleware_factory(app: FastAPI, limiter: RateLimiter) -> None:
    @app.middleware("http")
    async def ratelimit_middleware(request: Request, call_next):
        path = request.url.path
        if path in _EXCLUDED_PATHS:
            return await call_next(request)
        if not path.startswith(_RATELIMITED_PREFIXES):
            return await call_next(request)

        identifier = getattr(request.state, "user_id", None) or _client_ip(request)
        result = limiter.check(identifier)
        if not result.allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
                headers={"Retry-After": str(result.reset_in_seconds)},
            )
        return await call_next(request)


def create_app(
    kv: RedisKV | None = None,
    limit: int = _LIMIT,
    window_seconds: int = _WINDOW_SECONDS,
) -> FastAPI:
    app = FastAPI(title="myapi")
    real_kv: RedisKV = kv if kv is not None else RedisKVImpl()
    limiter = RateLimiter(kv=real_kv, limit=limit, window_seconds=window_seconds)

    # Starlette は後に登録した middleware が外側 = リクエストを先に受ける。
    # auth → ratelimit の順で評価したいので ratelimit を先・auth を後に登録する。
    _ratelimit_middleware_factory(app, limiter)
    _auth_middleware_factory(app)

    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(orders.router)
    return app


app = create_app()
