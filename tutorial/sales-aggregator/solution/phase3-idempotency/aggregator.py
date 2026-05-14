"""Phase 3 完了時の aggregator.py 全体像.

冪等性のために `processed_files` セットを管理する `IdempotentStore` を追加。
`CumulativeStore` は変更せず、`IdempotentStore` がその前段で取り込み判定する.
"""

from __future__ import annotations

from collections.abc import Iterable

from salesagg.models import ProductTotal, SaleRow
from salesagg.redis_kv import RedisKV

_PRODUCT_KEY_PREFIX = "app:report:product"
_PROCESSED_KEY = "app:report:processed_files"


def aggregate(rows: Iterable[SaleRow]) -> list[ProductTotal]:
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
    def __init__(self, kv: RedisKV) -> None:
        self._kv = kv

    def merge(self, batch: Iterable[ProductTotal]) -> None:
        for t in batch:
            key = f"{_PRODUCT_KEY_PREFIX}:{t.product_id}"
            self._kv.hincrby(key, "total_quantity", t.total_quantity)
            self._kv.hincrby(key, "total_amount", t.total_amount)

    def snapshot(self) -> list[ProductTotal]:
        out: list[ProductTotal] = []
        for key in sorted(self._kv.keys(f"{_PRODUCT_KEY_PREFIX}:*")):
            pid = key.removeprefix(f"{_PRODUCT_KEY_PREFIX}:")
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
        keys = self._kv.keys(f"{_PRODUCT_KEY_PREFIX}:*")
        if keys:
            self._kv.delete(*keys)


class IdempotentStore:
    """`idempotency_key` に対して取り込み済みかどうかを管理する.

    `try_mark_processed` が True を返した最初の 1 回だけ取り込みを実行する想定.
    """

    def __init__(self, kv: RedisKV) -> None:
        self._kv = kv

    def is_processed(self, idempotency_key: str) -> bool:
        return self._kv.sismember(_PROCESSED_KEY, idempotency_key)

    def try_mark_processed(self, idempotency_key: str) -> bool:
        """まだ処理されていなければ印を付けて True. すでに処理済みなら False."""
        return self._kv.sadd(_PROCESSED_KEY, idempotency_key) == 1

    def reset(self) -> None:
        self._kv.delete(_PROCESSED_KEY)
