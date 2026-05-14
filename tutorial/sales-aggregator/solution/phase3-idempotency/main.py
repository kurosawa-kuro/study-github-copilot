"""Phase 3 完了時の main.py 全体像.

idempotency key（既定: ファイル名）で同一ファイルの二重取り込みを抑止する.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import redis

from salesagg.aggregator import CumulativeStore, IdempotentStore, aggregate
from salesagg.csv_io import read_sales, write_report
from salesagg.redis_kv import RedisKV, RedisKVImpl


def _build_kv() -> RedisKV:
    return RedisKVImpl(client=redis.Redis(decode_responses=True))


def cli(argv: list[str] | None = None, kv: RedisKV | None = None) -> int:
    parser = argparse.ArgumentParser(prog="salesagg")
    parser.add_argument("--input", required=True, type=Path, help="入力 CSV パス")
    parser.add_argument("--output", required=True, type=Path, help="レポート出力 CSV パス")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="累積と処理済みマーカーをリセットしてから取り込む",
    )
    parser.add_argument(
        "--idempotency-key",
        default=None,
        help="二重取り込み抑止のキー（既定: 入力 CSV のファイル名）",
    )
    args = parser.parse_args(argv)

    kv_impl = kv if kv is not None else _build_kv()
    cumulative = CumulativeStore(kv_impl)
    idem = IdempotentStore(kv_impl)

    if args.reset:
        cumulative.reset()
        idem.reset()

    key = args.idempotency_key or args.input.name

    if idem.try_mark_processed(key):
        batch = aggregate(read_sales(args.input))
        cumulative.merge(batch)
        action = "merged"
    else:
        action = "skipped (already processed)"

    snapshot = cumulative.snapshot()
    write_report(args.output, snapshot)
    print(f"{action}: idempotency_key={key} / {len(snapshot)} totals -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(cli())
