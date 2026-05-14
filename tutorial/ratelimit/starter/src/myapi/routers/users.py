from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from myapi.core.redis_client import UserCacheRedis
from myapi.services.user_cache import fetch_user

router = APIRouter(prefix="/users", tags=["users"])


def get_cache() -> UserCacheRedis:
    return UserCacheRedis()


@router.get("/{user_id}")
def get_user(user_id: str, cache: UserCacheRedis = Depends(get_cache)) -> dict:
    user = fetch_user(user_id, cache)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user
