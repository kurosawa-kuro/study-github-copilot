# 日次売上集計レポート実装計画書

**プロジェクト**: study-github-copilot / sales-aggregator  
**作成日**: 2026-05-14  
**期限**: 2026-05-23  
**推奨所要時間**: 3〜5営業日  

---

## 全体概要

### 要件
- **入力**: 日次売上 CSV（product_id, quantity, unit_price, sold_at）
- **出力**: 商品ごとの累積レポート CSV
- **実行方式**: Python バッチスクリプト（毎朝実行想定）
- **永続化**: Redis により日次累積を引き継ぎ
- **冪等性**: 同一ファイルの二重投入を防止

### 実装戦略
3 つの Phase に分割し、各 Phase を 1 コミットで完結させます。積み上げ式で依存なし。

| Phase | 目的 | 工数 | リスク |
|---|---|---|---|
| 1 | Redis KV 抽象化層 | 1 日 | 低 |
| 2 | 累積マージ機構 | 1.5 日 | 中（データ整合性） |
| 3 | 冪等性機構 | 1 日 | 低 |

### Phase 間の依存関係
```
Phase 1 (RedisKV 抽象化)
    ↓
Phase 2 (CumulativeStore マージ)
    ↓
Phase 3 (IdempotentStore 冪等性)
```
※順序依存: Phase 3 は Phase 2 の成果物に `IdempotentStore` を追加する形

---

## Phase 1: Redis KV ラッパ抽象化

### 目的
集計の永続化に必要な最小限の Redis API を Protocol で抽象化し、テスト可能性を確保。既存動作は変えない（aggregator は未変更）。

### 前提
- starter/ の既存コード（models/csv_io/aggregator/main）が動作
- redis-py ≥5.0 と fakeredis ≥2.21 が依存関係に存在

### 変更/新規ファイル一覧

| パス | 種別 | 概要 | 想定行数 |
|---|---|---|---|
| `src/salesagg/redis_kv.py` | 新規 | RedisKV Protocol + RedisKVImpl 実装 | 55 |
| `tests/conftest.py` | 変更 | fake_kv fixture 追加 | +10 |
| `tests/test_redis_kv.py` | 新規 | RedisKV 正常系・異常系テスト | 45 |

**合計行数**: 約 110 行

### 公開インタフェース

```python
class RedisKV(Protocol):
    """集計・冪等性に必要な最小 API."""
    def hget(self, key: str, field: str) -> str | None: ...
    def hincrby(self, key: str, field: str, amount: int) -> int: ...
    def hgetall(self, key: str) -> dict[str, str]: ...
    def sismember(self, key: str, member: str) -> bool: ...
    def sadd(self, key: str, member: str) -> int: ...
    def keys(self, pattern: str) -> list[str]: ...
    def delete(self, *keys: str) -> int: ...


class RedisKVImpl:
    """redis-py のシンクラップ."""
    def __init__(self, client: redis.Redis | None = None) -> None: ...
    # 上記メソッド実装
```

### 完了条件

#### 機能条件
- `make run-sample` で既存動作と同一の CSV 集計ができる（aggregator は変更なし）
- `RedisKVImpl` を正しく初期化できる
- 全メソッド（hget/hincrby/hgetall/sismember/sadd/keys/delete）が実装

#### テスト条件
- `tests/test_redis_kv.py` の全テストがパス
- `tests/test_aggregator.py`（既存）も全パス（回帰なし）
- fake_kv fixture が正常に生成される

#### 検証コマンド
```bash
make verify  # lint + typecheck + test
```

### ロールバック手順
```bash
git revert HEAD  # 新規ファイルのみなので影響範囲最小
```

### 実装のポイント
- `redis.Redis` の戻り値をキャストして同期結果を確定（async 非対応）
- `decode_responses=True` で文字列として取得
- テストでは `fakeredis.FakeRedis` を使用

---

## Phase 2: 累積マージ機構

### 目的
商品ごとの累積を Redis に保持し、毎日新しい CSV を投入するたびに追加マージ。リセット機能でマニュアル初期化可能。

### 前提
- Phase 1 の `RedisKV` / `RedisKVImpl` が完成・テスト済み
- conftest.py に `fake_kv` fixture が存在

### 変更/新規ファイル一覧

| パス | 種別 | 概要 | 想定行数 |
|---|---|---|---|
| `src/salesagg/aggregator.py` | 変更 | `CumulativeStore` クラス追加（`aggregate` 関数は維持） | +40 |
| `src/salesagg/main.py` | 変更 | Redis 接続 + `CumulativeStore` 統合 + `--reset` CLI オプション | 交換 (↑20) |
| `tests/conftest.py` | 変更 | `sample_csv_day2` fixture 追加 | +15 |
| `tests/test_cumulative.py` | 新規 | 累積・リセット・CLI 統合テスト | 45 |

**合計行数**: 約 150 行

### 公開インタフェース

```python
class CumulativeStore:
    """Redis 上で商品ごとの累積集計を管理."""
    def __init__(self, kv: RedisKV) -> None: ...
    def merge(self, batch: Iterable[ProductTotal]) -> None:
        """バッチを累積に追加（加算）."""
    def snapshot(self) -> list[ProductTotal]:
        """現在の累積をスナップショット取得."""
    def reset(self) -> None:
        """累積をすべてクリア."""
```

### 完了条件

#### 機能条件
- 同じ CSV を 2 回投入すると累積値が **2 倍** になる（冪等性は Phase 3 で対処）
- 別日の CSV（sample_csv_day2）を投入すると累積が加算される
- `--reset` フラグ付きで実行すると累積がクリアされて新バッチから開始
- CLI 戻り値が 0 で、レポートが正しく出力されている

#### テスト条件
- `tests/test_cumulative.py` の全テストがパス
- 既存 `tests/test_aggregator.py` も全パス（`aggregate` 関数は変更なし）
- `test_csv_roundtrip` など既存テストが回帰なく動作

#### 検証コマンド
```bash
make verify  # lint + typecheck + test
```

### ロールバック手順
```bash
git revert HEAD  # aggregator.py と main.py を Phase 1 状態に戻す
```

### 注意（Phase 3 への引き継ぎ）
**[BREAKING]** 同じ CSV を 2 回投入すると二重計上される。Phase 3 で idempotency key 機構を導入して対処。

### 実装のポイント
- `_KEY_PREFIX = "app:report:product"` で命名規約統一
- `CumulativeStore.merge()` は `hincrby` で加算集計
- `snapshot()` で `hgetall` → `ProductTotal` 再構築
- Redis 接続失敗時は main.py で明示エラー（コンストラクタで例外発生）

---

## Phase 3: 冪等性機構（二重投入防止）

### 目的
Phase 2 の二重計上問題を解消。`idempotency_key`（既定: 入力ファイル名）で取り込み済みかを Redis Set に記録し、2 回目以降はスキップ。

### 前提
- Phase 2 の `CumulativeStore` が完成
- main.py の CLI がコマンドライン引数を受け取る形式を採用

### 変更/新規ファイル一覧

| パス | 種別 | 概要 | 想定行数 |
|---|---|---|---|
| `src/salesagg/aggregator.py` | 変更 | `IdempotentStore` クラス追加（`CumulativeStore` は変更なし） | +30 |
| `src/salesagg/main.py` | 変更 | `IdempotentStore` 統合 + `--idempotency-key` CLI オプション | 交換 (↑15) |
| `tests/test_idempotency.py` | 新規 | 冪等性・明示キー・リセット統合テスト | 55 |

**合計行数**: 約 130 行

### 公開インタフェース

```python
class IdempotentStore:
    """idempotency_key で取り込み済みかを管理."""
    def __init__(self, kv: RedisKV) -> None: ...
    def is_processed(self, idempotency_key: str) -> bool:
        """キーが既に処理済みか判定."""
    def try_mark_processed(self, idempotency_key: str) -> bool:
        """初回なら True + マーク. 2 回目以降は False."""
    def reset(self) -> None:
        """処理済みマーカーをすべてクリア."""
```

### 完了条件

#### 機能条件
- 同じ CSV を 2 回投入しても累積値が変化しない（冪等）
- `--idempotency-key` で明示指定すれば、同じファイルでも別キーなら取り込まれる（ユーザー意思の尊重）
- `--reset` で累積と冪等マーカーの **両方** がクリアされる
- CLI 出力に「merged」or「skipped」の区別が表示される

#### テスト条件
- `tests/test_idempotency.py` の全テストがパス
- `tests/test_cumulative.py`（Phase 2）も全パス（下位互換維持）
- `tests/test_aggregator.py`（既存）も全パス

#### 検証コマンド
```bash
make verify  # lint + typecheck + test
```

### ロールバック手順
```bash
git revert HEAD  # Phase 2 状態に戻す（累積マージは継続動作）
```

### 注意（範囲外事項）
- **[OUT-OF-SCOPE]** ファイル内容で重複判定する場合（同名の別内容ファイル）は別途ハッシュ化が必要
- **[QUESTION]** 冪等マーカーの TTL は無期限（Redis メモリ肥大の可能性あり）

### 実装のポイント
- `_PROCESSED_KEY = "app:report:processed_files"` で Set を一元管理
- `try_mark_processed()` が `sadd` の戻り値 1/0 を boolean に変換
- `--idempotency-key` が未指定なら `args.input.name`（ファイル名）をデフォルト

---

## 全体実行計画

### 推奨実行順
```
1. Phase 1 (Redis KV 抽象化)
   ↓ (Phase 1 完了・テストパス後)
2. Phase 2 (累積マージ)
   ↓ (Phase 2 完了・テストパス後)
3. Phase 3 (冪等性)
   ↓ (すべてテストパス)
4. E2E 検証 (`e2e/scenarios.sh` 実行)
```

### Phase 間の依存関係図

```mermaid
graph TD
    A["Phase 1<br/>RedisKV 抽象化<br/>1日"] -->|RedisKV Protocol| B["Phase 2<br/>CumulativeStore<br/>1.5日"]
    B -->|aggregate() 関数維持<br/>CumulativeStore 完成| C["Phase 3<br/>IdempotentStore<br/>1日"]
    C -->|全機能完成| D["E2E 検証<br/>scenarios.sh"]
    D -->|本番デプロイ準備|E["バッチスケジューラー連携<br/>cron/APScheduler/K8s"]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fce4ec
```

---

## リスク管理

### リスク一覧と対策

| リスク項目 | 発生条件 | 影響度 | 対策 | 検査方法 |
|---|---|---|---|---|
| **Redis 接続失敗** | デプロイ時 Redis 未起動 | 高 | main.py でスタックトレース出力 / ドキュメント記載 | `make redis-up` 確認 / 接続テスト |
| **キー名前空間競合** | マルチテナント環境 | 中 | `app:report:product:<id>` 命名規約を厳守 | CONVENTIONS.md 確認 / コードレビュー |
| **二重計上（Phase 2 残）** | Phase 3 未完成 | 中 | Phase 2 README に [BREAKING] 明記 / 本番投入前に Phase 3 必須 | test_cumulative.py で意図的にテスト |
| **冪等マーカー無限増加** | TTL 設定なし | 低 | [QUESTION] 運用ルール化待ち / 当面は問題ないサイズ | Redis INFO memory 監視予定 |
| **mypy strict 運用負荷** | 型注釈漏れ | 低 | pyproject.toml strict=true で即時検出 | `make typecheck` 必須 |
| **テストデータ不足** | エッジケース未検証 | 低 | conftest.py で複数日 CSV fixture 用意 | test_cumulative.py で日別テスト |

### 影響度レベル
- **高**: 本番停止 / データ喪失リスク
- **中**: 動作障害 / データ不整合
- **低**: 開発効率低下 / 潜在リスク

---

## 完了判定基準

### Phase ごとの完了チェックリスト

#### Phase 1 完了
- [ ] `src/salesagg/redis_kv.py` 実装完了（Protocol + RedisKVImpl）
- [ ] `tests/conftest.py` に fake_kv fixture 追加
- [ ] `tests/test_redis_kv.py` 全テストパス
- [ ] `make verify` で lint/typecheck/test 全パス
- [ ] `make run-sample` で既存動作と同一結果

#### Phase 2 完了
- [ ] `src/salesagg/aggregator.py` に CumulativeStore 追加
- [ ] `src/salesagg/main.py` Redis 接続 + CLI --reset 実装
- [ ] `tests/test_cumulative.py` 全テストパス
- [ ] 複数 CSV 投入で累積確認
- [ ] `--reset` で累積クリア確認
- [ ] `make verify` 全パス

#### Phase 3 完了
- [ ] `src/salesagg/aggregator.py` に IdempotentStore 追加
- [ ] `src/salesagg/main.py` に --idempotency-key 実装
- [ ] `tests/test_idempotency.py` 全テストパス
- [ ] 同一ファイル 2 回投入で冪等性確認
- [ ] `--reset` で冪等マーカー + 累積クリア確認
- [ ] `make verify` 全パス
- [ ] `e2e/scenarios.sh` 実行で E2E パス

---

## 中止判定条件

### 即座に中止すべき条件

| 条件 | 理由 | 代替案 |
|---|---|---|
| Redis 起動が環境で不可能 | インフラ制約 | SQLite への変更検討（ただし QUICK_GUIDE と乖離） |
| Python < 3.12 環境での動作必須 | バージョン制約 | pyproject.toml の requires-python を下げ + 型注釈互換性確認 |
| Pydantic < 2.0 環境で統合 | 依存ライブラリ競合 | コンフリクト解決 / 他プロジェクトとの調整 |

### 懸念で一時中断すべき条件

| 条件 | 判断目安 | 再開トリガー |
|---|---|---|
| Phase 2 テスト数が 20 以上必要 | 複雑度上昇の兆候 | テストカバレッジ ≥90% で再開 |
| Redis メモリ使用が 1GB 超過 | TTL 未設定のリスク | TTL 運用規則化まで本番延期 |
| 冪等性テストが 3 回以上失敗 | 要件理解不足 | 要件再確認ワークショップ → 再開 |

---

## 付録: 開発環境チェックリスト

### 初期セットアップ（Phase 1 開始前）

```bash
# 1. 既存テスト全パス確認
cd /home/ubuntu/repos/study-github-copilot/tutorial/sales-aggregator/starter
make verify

# 2. Redis 起動確認
make redis-up
redis-cli ping  # PONG が返る

# 3. fake_redis 動作確認
python -c "import fakeredis; print(fakeredis.__version__)"

# 4. 既存サンプル実行
make run-sample
cat data/output/report.csv
```

### 各 Phase 終了後の検証コマンド

```bash
# Phase 1 終了後
make verify
git log --oneline | head -1  # コミット確認

# Phase 2 終了後
make verify
./data/input/sales_2026-05-14.csv を 2 回投入 → 累積確認

# Phase 3 終了後
make verify
E2E テスト実行
bash e2e/scenarios.sh
```

---

## 参考資料

| ドキュメント | 用途 |
|---|---|
| [client-brief/request.md](../tutorial/sales-aggregator/client-brief/request.md) | 原要件書 |
| [QUICK_GUIDE.md](QUICK_GUIDE.md) | Step フロー全般 |
| [CONVENTIONS.md](../tutorial/sales-aggregator/starter/docs/CONVENTIONS.md) | コーディング規約 |
| [solution/phase1-3](../tutorial/sales-aggregator/solution/) | 実装参考例 |
| [e2e/scenarios.sh](../tutorial/sales-aggregator/e2e/scenarios.sh) | E2E 検証ハーネス |

---

## 進捗追跡テンプレート

```
2026-05-14: Phase 1 開始
2026-05-15: Phase 1 完了 / Phase 2 開始
2026-05-16: Phase 2 完了 / Phase 3 開始
2026-05-17: Phase 3 完了 / E2E 検証
2026-05-18: 本番デプロイ準備
2026-05-19-23: バッチスケジューラー連携 / 本番稼働開始
```

---

**承認者**: [未定]  
**レビュアー**: [未定]  
**更新履歴**: 2026-05-14 初版作成
