from __future__ import annotations

from fastapi import APIRouter

# NOTE: gateway 側で 600 req/min の制限がかかっている (infra-team 管理)。
# レートリミット導入時は二重制御になる点 + Retry-After / X-RateLimit-* ヘッダの
# 衝突回避を必ず検討すること。詳細は infra-team の Confluence「API Gateway 設定」参照。

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/{order_id}")
def get_order(order_id: str) -> dict:
    return {"id": order_id, "status": "shipped"}


@router.post("/")
def create_order(payload: dict) -> dict:
    return {"id": "o-new", **payload}
