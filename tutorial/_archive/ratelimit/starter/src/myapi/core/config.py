from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MYAPI_", extra="ignore")

    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    user_cache_ttl_seconds: int = Field(default=60)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
