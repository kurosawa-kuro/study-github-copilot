"""データモデル.

CSV のスキーマと集計レコードの形を pydantic で固定する.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SaleRow(BaseModel):
    """入力 CSV の 1 行."""

    sale_id: str
    product_id: str
    quantity: int = Field(ge=0)
    unit_price: int = Field(ge=0)  # NOTE: 通貨単位は要 [QUESTION]. 今は円・整数前提
    sold_at: datetime

    @property
    def amount(self) -> int:
        return self.quantity * self.unit_price


class ProductTotal(BaseModel):
    """商品ごとの集計結果."""

    product_id: str
    total_quantity: int
    total_amount: int
