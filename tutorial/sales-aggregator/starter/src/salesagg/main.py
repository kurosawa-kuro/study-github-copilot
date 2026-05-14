"""CLI エントリポイント.

Phase 0 (starter): 単一 CSV → 集計 → 別 CSV. 状態は持たない.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from salesagg.aggregator import aggregate
from salesagg.csv_io import read_sales, write_report


def cli() -> None:
    parser = argparse.ArgumentParser(prog="salesagg")
    parser.add_argument("--input", required=True, type=Path, help="入力 CSV パス")
    parser.add_argument("--output", required=True, type=Path, help="レポート出力 CSV パス")
    args = parser.parse_args()

    rows = list(read_sales(args.input))
    totals = aggregate(rows)
    write_report(args.output, totals)
    print(f"wrote {len(totals)} product totals to {args.output}")


if __name__ == "__main__":
    cli()
