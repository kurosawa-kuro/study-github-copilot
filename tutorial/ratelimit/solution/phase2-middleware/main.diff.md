# `main.py` への middleware 追加（要旨）

```python
EXCLUDED_PATHS = {"/health", "/openapi.json", "/docs"}
RATELIMITED_PREFIXES = ("/users", "/orders")


def _ratelimit_middleware_factory(app: FastAPI, limiter: RateLimiter) -> None:
    @app.middleware("http")
    async def ratelimit_middleware(request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)
        if not request.url.path.startswith(RATELIMITED_PREFIXES):
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


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
```

**登録順序が重要**: auth middleware の **後** に登録する（= `add_middleware` / `@middleware`
は LIFO 順実行なので、コード上は auth の後に書くと auth が先に走る）。

[ASSUMPTION] X-Forwarded-For 先頭を信頼する（ゲートウェイが上書きする前提）。
本番では信頼境界を Step 5-A で確認。
