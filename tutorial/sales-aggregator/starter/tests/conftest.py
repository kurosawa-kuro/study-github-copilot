from __future__ import annotations

from pathlib import Path

import fakeredis
import pytest


@pytest.fixture
def fake_redis() -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "sales.csv"
    p.write_text(
        "sale_id,product_id,quantity,unit_price,sold_at\n"
        "s-001,p-001,2,1500,2026-05-14T10:00:00+09:00\n"
        "s-002,p-002,1,3200,2026-05-14T11:00:00+09:00\n"
        "s-003,p-001,3,1500,2026-05-14T13:00:00+09:00\n",
        encoding="utf-8",
    )
    return p
