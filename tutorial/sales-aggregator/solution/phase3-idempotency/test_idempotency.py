"""Phase 3 で追加される冪等性テスト."""

from __future__ import annotations

from pathlib import Path

from salesagg.aggregator import IdempotentStore
from salesagg.main import cli
from salesagg.redis_kv import RedisKVImpl


def test_try_mark_processed_is_one_shot(fake_kv: RedisKVImpl) -> None:
    store = IdempotentStore(fake_kv)
    assert store.try_mark_processed("file-a") is True
    assert store.try_mark_processed("file-a") is False
    assert store.is_processed("file-a") is True


def test_reset_clears_processed(fake_kv: RedisKVImpl) -> None:
    store = IdempotentStore(fake_kv)
    store.try_mark_processed("file-a")
    store.reset()
    assert store.is_processed("file-a") is False


def test_cli_same_file_twice_does_not_double_count(
    fake_kv: RedisKVImpl, sample_csv: Path, tmp_path: Path
) -> None:
    out1 = tmp_path / "r1.csv"
    out2 = tmp_path / "r2.csv"

    cli(["--input", str(sample_csv), "--output", str(out1)], kv=fake_kv)
    cli(["--input", str(sample_csv), "--output", str(out2)], kv=fake_kv)

    text2 = out2.read_text(encoding="utf-8")
    # 二重取り込みされないので Phase 2 の累積と同じ値
    assert "p-001,5,7500" in text2
    assert "p-002,1,3200" in text2


def test_cli_different_files_accumulate(
    fake_kv: RedisKVImpl,
    sample_csv: Path,
    sample_csv_day2: Path,
    tmp_path: Path,
) -> None:
    out1 = tmp_path / "r1.csv"
    out2 = tmp_path / "r2.csv"

    cli(["--input", str(sample_csv), "--output", str(out1)], kv=fake_kv)
    cli(["--input", str(sample_csv_day2), "--output", str(out2)], kv=fake_kv)

    text2 = out2.read_text(encoding="utf-8")
    assert "p-001,6,9000" in text2  # 5 + 1
    assert "p-003,2,1960" in text2


def test_cli_explicit_idempotency_key_overrides_filename(
    fake_kv: RedisKVImpl, sample_csv: Path, tmp_path: Path
) -> None:
    out1 = tmp_path / "r1.csv"
    out2 = tmp_path / "r2.csv"

    cli(
        ["--input", str(sample_csv), "--output", str(out1), "--idempotency-key", "k-A"],
        kv=fake_kv,
    )
    # 別のキーで同じファイルを再投入 → 二重計上される（明示的にユーザーがキーを変えたため）
    cli(
        ["--input", str(sample_csv), "--output", str(out2), "--idempotency-key", "k-B"],
        kv=fake_kv,
    )

    text2 = out2.read_text(encoding="utf-8")
    assert "p-001,10,15000" in text2
