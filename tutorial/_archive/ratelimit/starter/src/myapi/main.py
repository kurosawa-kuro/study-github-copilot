from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from myapi.routers import health, orders, users


def _auth_middleware_factory(app: FastAPI) -> None:
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        # 認証不要パスは通す
        if request.url.path in {"/health", "/openapi.json", "/docs"}:
            return await call_next(request)
        auth = request.headers.get("authorization")
        if not auth or not auth.startswith("Bearer "):
            # NOTE: middleware 内では HTTPException が ExceptionMiddleware に拾われないため
            # 直接レスポンスを返す (Starlette ≥1.0 で挙動が顕在化)
            return JSONResponse(status_code=401, content={"detail": "unauthorized"})
        # 簡易: token == user_id とみなして state に積む
        request.state.user_id = auth.removeprefix("Bearer ").strip()
        return await call_next(request)


def create_app() -> FastAPI:
    app = FastAPI(title="myapi")
    _auth_middleware_factory(app)
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(orders.router)
    return app


app = create_app()
