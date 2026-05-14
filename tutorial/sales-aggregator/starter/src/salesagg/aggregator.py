"""集計ロジック (starter: 状態なし / 1 回きり集計).

NOTE (intentional design smell):
- このモジュールは入力 CSV を 1 つだけ受け取り、その範囲で集計する.
- 「過去の累積を引き継ぐ」要件には対応していない. 状態は完全にステートレス.
- レポートを差分マージしたい場合、永続化層を別途差し込む必要がある.
"""

from __future__ import annotations

from collections.abc import Iterable

from salesagg.models import ProductTotal, SaleRow


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
