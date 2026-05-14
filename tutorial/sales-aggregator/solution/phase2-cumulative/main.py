"""Phase 2 完了時の main.py 全体像.

CLI から累積モードを使えるようにする. Redis 接続失敗時は明示エラー.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import redis

from salesagg.aggregator import CumulativeStore, aggregate
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
        help="累積をリセットしてから取り込む（手動リセット用）",
    )
    args = parser.parse_args(argv)

    kv_impl = kv if kv is not None else _build_kv()
    store = CumulativeStore(kv_impl)

    if args.reset:
        store.reset()

    batch = aggregate(read_sales(args.input))
    store.merge(batch)
    snapshot = store.snapshot()
    write_report(args.output, snapshot)
    print(f"wrote {len(snapshot)} cumulative product totals to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(cli())
