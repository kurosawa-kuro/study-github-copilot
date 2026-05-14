# E2E 動作確認ハーネス

Phase 3 完了後の **Step 5-A 統合検証** で使う実行スクリプト。
受講者が「動く累積レポート」を体感し、Step 5-A の検証コマンドとして実行結果を引き継ぎに貼る。

## 前提

- Phase 1〜3 が完了している（solution と等価な状態）
- `docker compose` が使える

## 起動手順

```bash
cd tutorial/sales-aggregator/e2e
docker compose up -d          # Redis 起動
bash scenarios.sh             # 全シナリオ実行
docker compose down           # 後片付け
```

## シナリオ一覧

| # | 内容 | 期待 |
|---|---|---|
| 1 | 1 日目 CSV を取り込み | `p-001,5,7500` / `p-002,3,9600` / `p-003,1,980` |
| 2 | 同じ CSV を再取り込み | 値が変わらない（冪等） |
| 3 | 2 日目 CSV を取り込み | `p-001,6,9000` / `p-002,4,12800` / `p-003,5,4900` |
| 4 | `--idempotency-key reimport-1` で同じファイル再取り込み | `p-001,11,16500`（強制再取り込み） |
| 5 | `--reset` 付与で再取り込み | 累積も冪等マーカーもクリアされ、1 日目分のみ |

すべて pass で `All scenarios passed.` が出る。失敗時は該当シナリオ番号と理由が stderr に出る。

## 環境変数で変更可能

| 変数 | デフォルト | 用途 |
|---|---|---|
| `STARTER_DIR` | `../starter` | `salesagg` の実行ディレクトリ |
