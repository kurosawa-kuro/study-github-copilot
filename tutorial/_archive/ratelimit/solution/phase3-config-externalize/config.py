"""Phase 3 完了時の config.py 全体像.

`RatelimitSettings` を `Settings` に入れ子で追加し、環境変数からの上書きを可能にする。
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RatelimitSettings(BaseModel):
    limit: int = 60
    window_seconds: int = 60
    target_path_prefixes: tuple[str, ...] = ("/users", "/orders")
    excluded_paths: frozenset[str] = frozenset({"/health", "/openapi.json", "/docs"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MYAPI_",
        extra="ignore",
        env_nested_delimiter="__",
    )

    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    user_cache_ttl_seconds: int = Field(default=60)
    ratelimit: RatelimitSettings = Field(default_factory=RatelimitSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
