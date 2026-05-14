.PHONY: help install test test-quick lint typecheck verify run-sample clean

help:
	@echo "Targets:"
	@echo "  install      - uv sync --extra dev"
	@echo "  test         - 全テスト"
	@echo "  test-quick   - -x で失敗即停止"
	@echo "  lint         - ruff check"
	@echo "  typecheck    - mypy strict"
	@echo "  verify       - lint + typecheck + test (Phase 完了時)"
	@echo "  run-sample   - data/input/sales_2026-05-14.csv で実行 → data/output/report.csv"
	@echo "  redis-up     - docker compose で Redis 起動"
	@echo "  redis-down   - docker compose down"

install:
	uv sync --extra dev

test:
	uv run pytest -q

test-quick:
	uv run pytest -x -q

lint:
	uv run ruff check src tests

typecheck:
	uv run mypy src

verify: lint typecheck test
	@echo "verify OK"

run-sample:
	uv run salesagg --input data/input/sales_2026-05-14.csv --output data/output/report.csv

redis-up:
	docker compose up -d

redis-down:
	docker compose down
