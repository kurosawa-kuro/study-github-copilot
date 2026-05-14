# salesagg (starter)

日次の売上 CSV を取り込んで商品ごとに集計し、別 CSV に書き出す Python スクリプト。

## 構成

- Python 3.12 / redis-py / pydantic / pytest / fakeredis
- 依存管理: `pyproject.toml`（uv 想定）
- Redis: `compose.yaml` で起動（**現在の実装では未使用**。受講者がここに集計の状態を載せる）
- インフラ: ローカル開発のみ（クラウド・IaC は **本チュートリアルでは対象外**）

## 既知のメモ

- `src/salesagg/aggregator.py` は **状態を持たない**。1 ファイルを集計して終わり
- 「累積」を引き継ぎたい場合、永続化層が必要（コメントの design smell 参照）
- Redis は **インフラ的には既に用意済み**（`make redis-up` で立ち上がる）が、現コードは触っていない

## 開発

```bash
make install       # uv sync --extra dev
make test          # 全テスト
make verify        # lint + typecheck + test (Phase 完了時)
make run-sample    # data/input/sales_2026-05-14.csv → data/output/report.csv
make redis-up      # Redis を docker compose で起動
```

Makefile を使わない場合:

```bash
uv sync --extra dev
uv run pytest
uv run salesagg --input data/input/sales_2026-05-14.csv --output data/output/report.csv
```

## 規約

`docs/CONVENTIONS.md` を必ず読むこと。CSV 仕様・Redis キー命名・タグ運用・テスト方針が記載されている。
