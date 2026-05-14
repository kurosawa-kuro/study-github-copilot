from __future__ import annotations

from pathlib import Path

from salesagg.aggregator import aggregate
from salesagg.csv_io import read_sales, write_report
from salesagg.models import ProductTotal, SaleRow


def _row(pid: str, qty: int, price: int) -> SaleRow:
    return SaleRow.model_validate(
        {
            "sale_id": f"s-{pid}-{qty}",
            "product_id": pid,
            "quantity": qty,
            "unit_price": price,
            "sold_at": "2026-05-14T10:00:00+09:00",
        }
    )


def test_aggregate_sums_per_product() -> None:
    rows = [_row("p-001", 2, 1500), _row("p-001", 3, 1500), _row("p-002", 1, 3200)]
    result = aggregate(rows)
    by_id = {t.product_id: t for t in result}
    assert by_id["p-001"].total_quantity == 5
    assert by_id["p-001"].total_amount == 7500
    assert by_id["p-002"].total_quantity == 1
    assert by_id["p-002"].total_amount == 3200


def test_aggregate_empty_returns_empty_list() -> None:
    assert aggregate([]) == []


def test_csv_roundtrip(tmp_path: Path, sample_csv: Path) -> None:
    rows = list(read_sales(sample_csv))
    totals = aggregate(rows)
    out = tmp_path / "report.csv"
    write_report(out, totals)
    text = out.read_text(encoding="utf-8")
    assert text.startswith("product_id,total_quantity,total_amount\n")
    assert "p-001,5,7500" in text


def test_invalid_quantity_is_rejected() -> None:
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        SaleRow.model_validate(
            {
                "sale_id": "s-bad",
                "product_id": "p-001",
                "quantity": -1,
                "unit_price": 100,
                "sold_at": "2026-05-14T10:00:00+09:00",
            }
        )


def test_sample_csv_aggregation(sample_csv: Path) -> None:
    rows = list(read_sales(sample_csv))
    totals = {t.product_id: t for t in aggregate(rows)}
    assert totals["p-001"] == ProductTotal(product_id="p-001", total_quantity=5, total_amount=7500)
    assert totals["p-002"] == ProductTotal(product_id="p-002", total_quantity=1, total_amount=3200)
