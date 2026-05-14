"""Phase 2 完了時の aggregator.py 全体像.

ステートレス集計 (`aggregate`) は残し、累積を扱う `CumulativeStore` を追加した。
"""

from __future__ import annotations

from collections.abc import Iterable

from salesagg.models import ProductTotal, SaleRow
from salesagg.redis_kv import RedisKV

_KEY_PREFIX = "app:report:product"


def aggregate(rows: Iterable[SaleRow]) -> list[ProductTotal]:
    """starter から維持. 単一バッチの集計."""
    quantities: dict[str, int] = {}
    amounts: dict[str, int] = {}
    for row in rows:
        quantities[row.product_id] = quantities.get(row.product_id, 0) + row.quantity
        amounts[row.product_id] = amounts.get(row.product_id, 0) + row.amount
    return [
        ProductTotal(
            product_id=pid,
            total_quantity=quantities[pid],
            total_amount=amounts[pid],
        )
        for pid in sorted(quantities.keys())
    ]


class CumulativeStore:
    """商品ごとの累積集計を Redis に保持し、新しいバッチをマージする."""

    def __init__(self, kv: RedisKV) -> None:
        self._kv = kv

    def merge(self, batch: Iterable[ProductTotal]) -> None:
        for t in batch:
            key = f"{_KEY_PREFIX}:{t.product_id}"
            self._kv.hincrby(key, "total_quantity", t.total_quantity)
            self._kv.hincrby(key, "total_amount", t.total_amount)

    def snapshot(self) -> list[ProductTotal]:
        out: list[ProductTotal] = []
        for key in sorted(self._kv.keys(f"{_KEY_PREFIX}:*")):
            pid = key.removeprefix(f"{_KEY_PREFIX}:")
            data = self._kv.hgetall(key)
            out.append(
                ProductTotal(
                    product_id=pid,
                    total_quantity=int(data.get("total_quantity", "0")),
                    total_amount=int(data.get("total_amount", "0")),
                )
            )
        return out

    def reset(self) -> None:
        keys = self._kv.keys(f"{_KEY_PREFIX}:*")
        if keys:
            self._kv.delete(*keys)
