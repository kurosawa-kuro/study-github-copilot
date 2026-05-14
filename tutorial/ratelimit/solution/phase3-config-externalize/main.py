"""Phase 3 完了時の main.py 全体像.

Phase 2 のハードコード値を `get_settings().ratelimit` 経由に置換し、
`X-RateLimit-Limit / Remaining / Reset` を成功応答にも付与する。
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from myapi.core.config import RatelimitSettings, get_settings
from myapi.core.ratelimit import RateLimiter
from myapi.core.redis_kv import RedisKV, RedisKVImpl
from myapi.routers import health, orders, users


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _auth_middleware_factory(app: FastAPI, cfg: RatelimitSettings) -> None:
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        if request.url.path in cfg.excluded_paths:
            return await call_next(request)
        auth = request.headers.get("authorization")
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "unauthorized"})
        request.state.user_id = auth.removeprefix("Bearer ").strip()
        return await call_next(request)


def _ratelimit_middleware_factory(
    app: FastAPI, limiter: RateLimiter, cfg: RatelimitSettings
) -> None:
    @app.middleware("http")
    async def ratelimit_middleware(request: Request, call_next):
        path = request.url.path
        if path in cfg.excluded_paths:
            return await call_next(request)
        if not path.startswith(cfg.target_path_prefixes):
            return await call_next(request)

        identifier = getattr(request.state, "user_id", None) or _client_ip(request)
        result = limiter.check(identifier)
        headers = {
            "X-RateLimit-Limit": str(cfg.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(result.reset_in_seconds),
        }
        if not result.allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
                headers={**headers, "Retry-After": str(result.reset_in_seconds)},
            )
        response = await call_next(request)
        for k, v in headers.items():
            response.headers[k] = v
        return response


def create_app(kv: RedisKV | None = None, cfg: RatelimitSettings | None = None) -> FastAPI:
    app = FastAPI(title="myapi")
    real_cfg = cfg if cfg is not None else get_settings().ratelimit
    real_kv: RedisKV = kv if kv is not None else RedisKVImpl()
    limiter = RateLimiter(
        kv=real_kv, limit=real_cfg.limit, window_seconds=real_cfg.window_seconds
    )

    _ratelimit_middleware_factory(app, limiter, real_cfg)
    _auth_middleware_factory(app, real_cfg)

    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(orders.router)
    return app


app = create_app()
