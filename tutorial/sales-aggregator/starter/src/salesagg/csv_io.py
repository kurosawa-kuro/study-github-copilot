"""CSV の読み書き."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator
from pathlib import Path

from salesagg.models import ProductTotal, SaleRow


def read_sales(path: Path) -> Iterator[SaleRow]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield SaleRow.model_validate(row)


def write_report(path: Path, totals: Iterable[ProductTotal]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["product_id", "total_quantity", "total_amount"])
        for t in totals:
            writer.writerow([t.product_id, t.total_quantity, t.total_amount])
