# リファクタリング項目

プロジェクト評価（2026-05-14）で特定した、構造的に直すべき箇所をまとめる。
新規機能追加・教材追加は別管理（本書ではスコープ外）。

優先度の凡例:

- **P1**: 整合性・運用安全に直結。次の改訂で着手推奨
- **P2**: 中長期で品質が劣化する原因。v4 までに対処
- **P3**: 細部の一貫性。気づいたタイミングで合わせる

---

## R1. ドキュメント正本の一元化【P1】

### 現状

同一情報が 3 ファイルに重複している:

| 情報 | README.md | docs/QUICK_GUIDE.md | docs/PROMPT_TEMPLATE.md |
|---|---|---|---|
| 規模別フロー表 | ◯ | ◯ | ◯（運用上の留意点で間接的に） |
| 戻り先判定表 | ◯ | ◯（Step 4 のとは別文言） | ◯（Step 4 本文） |
| タグ一覧 | △（部分） | ◯ | ◯（Step 0-C 内） |
| 段階導入ガイド | ◯ | ✗ | ◯ |
| 領域別の適用差 | ◯ | ✗ | ◯ |

CLAUDE.md には「片方を編集したらもう片方の整合性を必ず確認」とあるが、機械的な担保が無く、編集ミスで矛盾する余地が大きい。

### 問題

- 戻り先判定表が QUICK_GUIDE と PROMPT_TEMPLATE で表現が違う（[QUICK_GUIDE.md L27-33](QUICK_GUIDE.md#L27-L33) vs [PROMPT_TEMPLATE.md L272-278](PROMPT_TEMPLATE.md#L272-L278)）
- バージョン改訂時に同じ表を 3 箇所更新する必要があり、漏れが必ず起きる
- 新メンバーが「どれが最新か」を判別できない

### 提案

**QUICK_GUIDE.md を Step 本文・表類の単一正本とする**。役割を以下に再整理:

| ファイル | 担当範囲 |
|---|---|
| `README.md` | プロジェクト全体ナビ・使い方・ディレクトリ構成のみ。表類は QUICK_GUIDE への参照に置き換え |
| `docs/QUICK_GUIDE.md` | Step 本文・規模別フロー・タグ・戻り先判定（**実運用で貼り付ける一次資料**） |
| `docs/PROMPT_TEMPLATE.md` | v3 設計仕様（背景・工程全体マップ・運用上の留意点・段階導入ガイド・領域別適用差・改訂履歴）のみ。Step 本文は QUICK_GUIDE への相対リンクで参照 |

### 影響範囲

- `README.md` の規模別フロー表 → QUICK_GUIDE への参照に変更
- `PROMPT_TEMPLATE.md` の Step 0-A / 0-C / 1〜5 本文（L67-370 相当） → 削除し QUICK_GUIDE 参照リンクに置換
- `CLAUDE.md` の「ドキュメント編集時の注意」を「QUICK_GUIDE.md が Step 本文の正本」に書き直し

### 受け入れ条件

- 同一の表・プロンプト本文が 2 箇所以上に存在しない
- `grep "規模別フロー\|戻り先判定" docs/ README.md` で正本が 1 箇所のみ

---

## R2. `solution/` の形式統一【P1】

### 現状

模範解答の表現形式が Phase ごとにバラついている:

| Phase | コード成果物の形式 |
|---|---|
| 1 | `redis_kv.py`（完全ファイル）+ `redis_client.diff.md`（要旨のみ） |
| 2 | `ratelimit.py`（完全ファイル）+ `main.diff.md`（要旨のみ） |
| 3 | `README.md` のみ。実コードファイルなし |

### 問題

- ファシリが「正解」と照合するときに情報量が揃わない（Phase 3 は `.env.example` や `test_ratelimit.py` の実差分が確認できない）
- 受講者が誤って覗いた場合、Phase 1/2 と 3 で「どこまでコードが書かれているか」の体験が異なる
- 差分要旨（`*.diff.md`）と完全ファイルの併存ルールが不明

### 提案

いずれかに方針を決め切る:

- **案 A（推奨）**: 全 Phase で「完全成果物ファイル」＋「README（完了条件・検証コマンド・引き継ぎ JSON への参照）」の 2 種類に統一。`*.diff.md` は廃止
- 案 B: 全 Phase で「README + 差分要旨 `*.diff.md`」に統一し、完全ファイルは置かない

案 A は採点容易性、案 B は容量小・差分の意図が明確、というトレードオフ。`solution/README.md` の現状記述（「Phase ごとに 1 ディレクトリ = 1 コミット相当」）を尊重するなら案 A が整合する。

### 影響範囲（案 A 採用時）

- `solution/phase1-redis-abstraction/redis_client.diff.md` → `redis_client.py`（完全ファイル）に置換
- `solution/phase2-middleware/main.diff.md` → `main.py`（完全ファイル）に置換
- `solution/phase3-config-externalize/` に `config.py` / `main.py` / `test_ratelimit.py` / `.env.example` を追加

### 受け入れ条件

- `find solution -name "*.diff.md"` が空（案 A の場合）
- 各 Phase ディレクトリのファイル種類が同型

---

## R3. 「保留」Step の扱い明文化【P2】

### 現状

- Step 0-B（設計判断）と Step 5-C（振り返り）は意図的に未整備
- [PROMPT_TEMPLATE.md L367-368](PROMPT_TEMPLATE.md#L367-L368) で「複数案件で同種の問題が再発したら整備」とあるが、定性的でトリガが不明瞭

### 問題

- 「保留」が事実上の「永遠に未整備」に化けるリスク
- 戻り先判定表に「0-B（再設計）」が含まれているのに本文が無い、という不整合（[QUICK_GUIDE.md L32](QUICK_GUIDE.md#L32) / Step 4 戻り先表）

### 提案

以下のどちらかを採る:

- **案 A（推奨）**: 整備トリガを定量化して明記
  - 例: 「アーキテクチャ判断を必要とする案件が 2 件以上発生したら 0-B を整備」「同種の Step 4 戻り先判定が 3 件以上再発したら 5-C を整備」
- 案 B: 「v3 のスコープでは未着手。代替として Step 0-A の `[AMBIGUITY]` 列挙で吸収する」と明示し、戻り先判定表からも 0-B を削除

中途半端な「保留」は劣化が早い。どちらかに倒す。

### 影響範囲

- `PROMPT_TEMPLATE.md` の Step 0-B / 5-C セクション
- `QUICK_GUIDE.md` の戻り先判定表（案 B 採用時は「設計欠陥 → Step 0-B」の行を削除または「Step 1 影響範囲再調査」に変更）

---

## R4. 改訂履歴・バージョン整合【P2】

### 現状

- 改訂履歴は `PROMPT_TEMPLATE.md` のみで管理（v1 / v2 / v3）
- `README.md` の改訂履歴セクションは同内容を重複保持
- `QUICK_GUIDE.md` / `CLAUDE.md` には改訂履歴が無く、対応バージョンが分からない

### 問題

- v4 で Step 構成が変わるとき、どのファイルが追随済みか判別不能
- README と PROMPT_TEMPLATE の改訂履歴が将来ズレる

### 提案

- 改訂履歴は `PROMPT_TEMPLATE.md` を単一正本とし、`README.md` 側は削除＋リンク化
- 各ファイル冒頭に `<!-- v3 / 対応: PROMPT_TEMPLATE.md v3 -->` のような対応バージョンコメントを追加
- v4 改訂時は「PROMPT_TEMPLATE → QUICK_GUIDE → README → CLAUDE → tutorial」の順で更新するルールを `CLAUDE.md` に明記

### 影響範囲

- `README.md` L145-149（改訂履歴セクション）
- `CLAUDE.md` に更新順序ルールを追加

---

## R5. Step 0-C テンプレの冗長性低減【P2】

### 現状

[QUICK_GUIDE.md L75-111](QUICK_GUIDE.md#L75-L111) の Step 0-C は約 40 行で、技術スタック列挙・コーディング規約・制約・出力ルールが全部入り。

### 問題

- 「Phase 開始時にコンテキスト落ち対策で再貼り付け」推奨だが、毎 Phase 40 行貼るのは現実的に重い
- 案件ごとに `[例: ...]` の置換箇所が多く、テンプレ自体に揺らぎが生じる
- CLAUDE.md の「starter のコーディング規約」も似た情報を持っており重複

### 提案

Step 0-C を 2 段構成に分割:

- **0-C-min**（コア・10 行程度）: 言語・依存管理・テスト・タグルール・後方互換性。**Phase ごとに再貼り付け**
- **0-C-full**（現状の 40 行）: セッション開始時に 1 回のみ。プロジェクト固有の値を埋めた成果物を `docs/CONTEXT.md` 等に保存する想定

または、`docs/` 配下にプロジェクト用の埋め込み済み Step 0-C テンプレ（テンプレートではなく実値版）を置く運用にする。

### 影響範囲

- `QUICK_GUIDE.md` の Step 0-C セクション分割
- `PROMPT_TEMPLATE.md` の Step 0-C 本文（R1 で QUICK_GUIDE 参照化するなら自動追随）

---

## R6. 細部の一貫性【P3】

以下は気づいたタイミングで合わせる粒度:

| 箇所 | 問題 | 修正 |
|---|---|---|
| [QUICK_GUIDE.md L84](QUICK_GUIDE.md#L84) | Memorystore (Standard) は永続化が弱くジョブキュー向きではない | 用途リストから「ジョブキュー」を削るか `[要件次第で自前運用]` 注記 |
| `tutorial/ratelimit/facilitator-guide/99-rubric.md` L27 | 監視・アラートを Non-Goal としているが、大規模フロー（5-B）では本来必須 | 「本教材スコープでは Non-Goal、実案件では別チケット化必須」と注記 |
| `tutorial/ratelimit/starter/pyproject.toml` | `pythonpath = ["src"]` 設定はあるが `[tool.ruff.lint]` / `[tool.mypy]` の対象範囲明示なし | ruff の `src` 指定、mypy の `files = ["src"]` を追記 |
| `tutorial/ratelimit/starter/README.md` L20-24 | `uv sync` のみ。`--extra dev` がない（テスト実行に必須） | `uv sync --extra dev` に修正（`facilitator-guide/00-setup.md` とは整合している） |
| `tutorial/ratelimit/solution/handoff-jsons/phase*.json` | Phase 1 / 3 のサンプル内容を読まないと判別できないファイル名 | README に各 JSON の要点（key_decisions の例）を一覧化 |

---

## 着手順序（提案）

1. **R2**（solution 統一）— 教材として欠落が一番目立つ。1〜2 時間で完了
2. **R1**（正本一元化）— 改訂運用の土台。R3 / R4 / R5 が R1 の上に乗る
3. **R3**（保留 Step）+ **R4**（改訂履歴）— セットで方針決定
4. **R5**（Step 0-C 分割）— R1 完了後に着手
5. **R6**（細部）— 上記の作業中に都度
