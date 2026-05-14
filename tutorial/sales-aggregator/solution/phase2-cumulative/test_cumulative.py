"""Phase 2 で追加される累積マージのテスト."""

from __future__ import annotations

from pathlib import Path

from salesagg.aggregator import CumulativeStore, aggregate
from salesagg.csv_io import read_sales
from salesagg.main import cli
from salesagg.redis_kv import RedisKVImpl


def test_merge_adds_to_existing_totals(fake_kv: RedisKVImpl, sample_csv: Path) -> None:
    store = CumulativeStore(fake_kv)
    batch = aggregate(read_sales(sample_csv))
    store.merge(batch)

    snap = {t.product_id: t for t in store.snapshot()}
    assert snap["p-001"].total_quantity == 5
    assert snap["p-001"].total_amount == 7500
    assert snap["p-002"].total_quantity == 1
    assert snap["p-002"].total_amount == 3200


def test_merge_is_additive_over_multiple_batches(
    fake_kv: RedisKVImpl, sample_csv: Path, sample_csv_day2: Path
) -> None:
    store = CumulativeStore(fake_kv)
    store.merge(aggregate(read_sales(sample_csv)))
    store.merge(aggregate(read_sales(sample_csv_day2)))

    snap = {t.product_id: t for t in store.snapshot()}
    assert snap["p-001"].total_quantity == 6  # 5 + 1
    assert snap["p-001"].total_amount == 9000  # 7500 + 1500
    assert snap["p-003"].total_quantity == 2
    assert snap["p-003"].total_amount == 1960


def test_reset_clears_all(fake_kv: RedisKVImpl, sample_csv: Path) -> None:
    store = CumulativeStore(fake_kv)
    store.merge(aggregate(read_sales(sample_csv)))
    store.reset()
    assert store.snapshot() == []


def test_cli_writes_cumulative_report(
    fake_kv: RedisKVImpl,
    sample_csv: Path,
    sample_csv_day2: Path,
    tmp_path: Path,
) -> None:
    out1 = tmp_path / "r1.csv"
    out2 = tmp_path / "r2.csv"

    assert cli(["--input", str(sample_csv), "--output", str(out1)], kv=fake_kv) == 0
    assert cli(["--input", str(sample_csv_day2), "--output", str(out2)], kv=fake_kv) == 0

    text2 = out2.read_text(encoding="utf-8")
    assert "p-001,6,9000" in text2  # 累積している
    assert "p-003,2,1960" in text2
