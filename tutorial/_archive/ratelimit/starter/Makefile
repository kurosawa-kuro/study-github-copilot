.PHONY: help install test test-quick test-compat test-ratelimit lint typecheck verify run clean

help:
	@echo "Targets:"
	@echo "  install        - uv sync --extra dev"
	@echo "  test           - 全テスト"
	@echo "  test-quick     - -x で失敗即停止 (Phase 開発中向け)"
	@echo "  test-compat    - 後方互換性のみ (Phase 1 完了確認用)"
	@echo "  test-ratelimit - レートリミット関連のみ (Phase 2 / 3)"
	@echo "  lint           - ruff check"
	@echo "  typecheck      - mypy strict"
	@echo "  verify         - lint + typecheck + test (Phase 完了時)"
	@echo "  run            - uvicorn 起動"

install:
	uv sync --extra dev

test:
	uv run pytest -q

test-quick:
	uv run pytest -x -q

test-compat:
	uv run pytest tests/test_compat.py -v

test-ratelimit:
	uv run pytest tests/test_ratelimit.py -v

lint:
	uv run ruff check src tests

typecheck:
	uv run mypy src

verify: lint typecheck test
	@echo "verify OK"

run:
	uv run uvicorn myapi.main:app --reload
