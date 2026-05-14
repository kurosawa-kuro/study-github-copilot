# 学習教材・チュートリアルとしてのリファクタリング項目

`tutorial/ratelimit/` を **学習教材・ハンズオン教材** として運用したときに見えてくる構造的な欠点をまとめる。
ドキュメント体系全体のリファクタは [REFACTORING.md](REFACTORING.md) を参照。

優先度:

- **P1**: 学習効果に直結。次の受講者が来る前に直す
- **P2**: ファシリ運用負荷を増やす要因。中期で対処
- **P3**: 体験品質の改善。気づいたタイミングで

---

## T1. 自学自習動線の欠落【P1】

### 現状

`tutorial/ratelimit/` は **ファシリ前提** で設計されている:

- `client-brief/` が薄い → ファシリが `[QUESTION]` の想定回答を返す
- `facilitator-guide/` がレビュー基準を独占
- `solution/` は「受講者は見ない」と注意書きされている（[solution/README.md L19](../tutorial/ratelimit/solution/README.md#L19)）
- `00-setup.md` で「ペア／モブ推奨」と明記

しかし現実の利用者には **一人で進めたい受講者**（社内研修の事前学習、独学）が確実に存在する。

### 問題

- 自学自習者は `[QUESTION]` への回答を誰からも得られず、Step 0-A の練習が完結しない
- 「solution を見ない」というルールは git クローンの中身が丸見えな状況では機能しない（強い意志に依存）
- ファシリ運用と自学運用で動線が混ざり、どちらも中途半端になりがち

### 提案

`tutorial/ratelimit/` の運用モードを 2 つ明示分離する:

| モード | 入力 | レビュー |
|---|---|---|
| **A. ファシリ運用** | `client-brief/` の薄い依頼書 | ファシリが `01-step0a-expected-questions.md` で添削 |
| **B. 自学自習** | `client-brief-extended/`（仮想クライアント回答付き Q&A 形式） | `self-review/` に各 Step の自己採点シート |

具体策:

1. `tutorial/ratelimit/client-brief/` に `2026-05-14_ratelimit.md`（薄い・現状）と `2026-05-15_ratelimit_qa.md`（受講者が `[QUESTION]` を投げた後の想定回答が記録された Q&A ログ）の 2 種を置く
2. `facilitator-guide/01-step0a-expected-questions.md` の「想定回答」列だけを抽出した `self-review/step0a-answers.md` を新設
3. `tutorial/ratelimit/README.md` の「進め方」を **モード A / モード B 別** に書き直す

### 受け入れ条件

- ファシリ無しで 8〜12 時間の標準フローを通せる手順書が存在
- 自学者が `solution/` を覗かずに Step 0-A〜5-A まで自己採点できる

---

## T2. 戻り先判定の「強制度」が高すぎる【P1】

### 現状

[facilitator-guide/05-step3-4-loop.md L51-58](../tutorial/ratelimit/facilitator-guide/05-step3-4-loop.md#L51-L58) は「最低 1 回は戻り先判定を起こさせる」を明記し、Phase 2 の middleware 順序問題が **ほぼ確実に起きる** ように仕込まれている:

- `starter/main.py` で auth middleware が既に登録済み → 順序を意識せず実装すると壊れる
- gateway 600 req/min の伏線 → Step 1 で見落とすと Phase 2 で `[BREAKING]` 発覚

### 問題

- 戻り先判定は **受講者の判断力** を試すための装置なのに、ほぼ強制発火する構造になっており、判断練習にならない
- 「戻り先判定が 1 回以上発生 = A 評価」（[99-rubric.md L7](../tutorial/ratelimit/facilitator-guide/99-rubric.md#L7)）なので、仕掛けに引っかかるだけで A が取れる
- 学習として最も価値があるのは「戻り先判定を **しないで済むよう Step 2 で先回り** する」体験。現状は逆方向に最適化されている

### 提案

戻り先判定の練習機会を **3 段階の難易度** に分ける:

| 難易度 | 受講者の体験 |
|---|---|
| **易**: 仕掛け通りに戻る | Phase 2 で順序問題に当たり Step 2 に戻る（現状） |
| **中**: 仕掛けに気づいて Step 2 で予防 | `99-rubric.md` の「加点ボーナス +1」を中難易度の必達条件に格上げ |
| **難**: 別の戻り先判定を自発的に起こす | Phase 3 で `X-RateLimit-Reset` の単位（epoch vs 残秒）が曖昧 → Step 0-A 戻り、等の追加シナリオを `facilitator-guide/05-step3-4-loop.md` に追記 |

評価ルーブリックも以下に再設計:

- **A**: 戻り先判定を **予防** または **自発的に発見** ＋ 全 Step 通過
- **B**: 仕掛けに引っかかって戻り先判定を経験 ＋ 全 Step 通過（= 現状の A）
- **C**: 戻り先判定なしで完走（仕掛けを見落とした）

### 影響範囲

- `tutorial/ratelimit/facilitator-guide/99-rubric.md` の総合評価表
- `facilitator-guide/05-step3-4-loop.md` に「難」シナリオ追加

---

## T3. Phase 3 完了後の動作確認体験が無い【P1】

### 現状

- `solution/phase3-config-externalize/` は README のみ。実コードが無い
- E2E シナリオは [facilitator-guide/06-step5a-integration.md L19-26](../tutorial/ratelimit/facilitator-guide/06-step5a-integration.md#L19-L26) に表で記載されているが、**実行スクリプトが無い**
- 受講者が「動くもの」を立ち上げて 60 回 curl を叩く手順は口頭・テキストでのみ

### 問題

- せっかく実装したレートリミッタを **動かして体感する** 機会が無い
- `Retry-After: 60` がレスポンスに乗る瞬間や、`X-RateLimit-Remaining` が減っていく挙動を見るのが、この教材の最大の報酬のはず
- Step 5-A の E2E が「テキストで結果を書け」止まりで、検証コマンドが提供されていない

### 提案

`tutorial/ratelimit/` 配下に **動作確認ハーネス** を追加:

```
tutorial/ratelimit/
├── e2e/
│   ├── README.md            # シナリオ一覧と期待結果
│   ├── scenarios.sh         # curl ループ × 5 シナリオ
│   └── compose.yaml         # myapi + redis を立ち上げ（fakeredis 不可なので本物 redis）
```

スクリプト構成:

- シナリオ 1: 認証あり `/users/u-001` × 60 回 → 全 200
- シナリオ 2: 61 回目 → 429 + `Retry-After`
- シナリオ 3: `/health` × 100 回 → 全 200、ヘッダなし
- シナリオ 4: 異なる user_id でカウンタ独立
- シナリオ 5: 窓リセット待機（60 秒スリープ → 再度 60 回成功）

### 受け入れ条件

- `bash e2e/scenarios.sh` で全シナリオが pass/fail 判定付きで実行できる
- Phase 3 終了後に Step 5-A の検証コマンドとして `e2e/scenarios.sh` が指定されている

---

## T4. solution/ の Phase 3 不完全【P1】

### 現状

`solution/phase1-redis-abstraction/` と `phase2-middleware/` は実コードがあるが、`phase3-config-externalize/` は README のみ。

- 受講者が Phase 3 で詰まったときの参照先が無い
- ファシリも Phase 3 の採点は README の記述だけで照合することになる

### 提案

[REFACTORING.md R2](REFACTORING.md) と統合。Phase 3 にも以下を追加:

- `config.py`（完全成果物）
- `main.py`（middleware にヘッダ付与した完全版）
- `test_ratelimit.py` の差分または完全版
- `.env.example`

### 影響範囲

- `tutorial/ratelimit/solution/phase3-config-externalize/`

---

## T5. starter の罠と既存テストの強度【P2】

### 現状

[starter/tests/test_users.py](../tutorial/ratelimit/starter/tests/test_users.py) / [test_orders.py](../tutorial/ratelimit/starter/tests/test_orders.py) は **正常系・1 異常系のみ**:

- `test_get_user_ok` / `test_get_user_not_found` / `test_get_user_unauthorized`
- `test_get_order_ok` / `test_health_no_auth`

### 問題

- 後方互換性を壊さない練習が中核（CLAUDE.md でも明記）なのに、テストが薄すぎて壊しても気づきにくい
- 例: `UserCacheRedis.__init__` のシグネチャを変えても、テストは `conftest.py` の fixture 経由なので壊れない
- レートリミット導入時に既存テストが「全部 1 回しか叩かない」ので、レート制限に引っかかる事故も観察できない

### 提案

starter の既存テストを **後方互換性検出器** として強化:

```python
# tests/test_compat.py（新規）

def test_user_cache_constructor_signature():
    """UserCacheRedis(client=...) で初期化できることを契約とする"""
    import inspect
    sig = inspect.signature(UserCacheRedis.__init__)
    assert "client" in sig.parameters  # Phase 1 で kv に変えるとここで FAIL

def test_users_endpoint_under_high_load(client, auth_headers):
    """同一ユーザーで 100 回叩いても 200 が返る（= レート制限が無い状態）"""
    for _ in range(100):
        resp = client.get("/users/u-001", headers=auth_headers)
        assert resp.status_code == 200
    # Phase 2 でレートリミット入れると FAIL → テスト側を更新する判断が要る
```

このテストが入っていれば:

- Phase 1 のシグネチャ変更を `[BREAKING]` として検出できる
- Phase 2 で「既存テストを変更する → `[BREAKING]` 報告」のフローを実体験できる

### 受け入れ条件

- starter で `uv run pytest -q` が緑
- Phase 1 完了時点で `test_compat.py` の状態が変化しない（外部 API 不変が確認できる）

---

## T6. 検証コマンド実行の足回り【P2】

### 現状

- 検証コマンドは `uv run pytest -q` / `MYAPI_RATELIMIT_LIMIT=5 uv run pytest tests/test_ratelimit.py -q` 等
- 直書きで散らばっており、Phase ごとにコピペ依存

### 問題

- 受講者がコマンドを写し間違える
- 「検証コマンドの実行結果を貼り付け」（[QUICK_GUIDE.md L181](QUICK_GUIDE.md#L181)）が肝心なのに、実行の手間が高い

### 提案

`starter/Makefile`（または `tasks.py`）を追加:

```makefile
.PHONY: test test-ratelimit test-compat lint typecheck verify

test:
	uv run pytest -q

test-ratelimit:
	MYAPI_RATELIMIT_LIMIT=5 uv run pytest tests/test_ratelimit.py -q

verify:  ## Phase 完了時の全自動検証
	$(MAKE) lint typecheck test

lint:
	uv run ruff check src tests

typecheck:
	uv run mypy src
```

各 Phase の完了条件「検証コマンド」を `make verify` 等に統一すると、引き継ぎ JSON の検証コマンド欄も統一できる。

### 影響範囲

- `tutorial/ratelimit/starter/Makefile` 新設
- `solution/phase{1,2,3}-*/README.md` の検証コマンド表記統一

---

## T7. ふりかえりの構造化【P2】

### 現状

[99-rubric.md L63-68](../tutorial/ratelimit/facilitator-guide/99-rubric.md#L63-L68) のふりかえり質問:

1. 一番効いた Step はどれか？
2. 戻り先判定が発生したのは Phase いくつ？
3. 依頼書の薄さに対して、何個の `[QUESTION]` を返した？
4. solution 通りに進めなかった部分の判断根拠は？

### 問題

- 質問だけあって回答テンプレ・記入欄が無い
- 受講者がふりかえりを書いても、ファシリが横並びで比較できない
- 学習資産として蓄積されない

### 提案

`tutorial/ratelimit/retrospective/` を新設:

```
tutorial/ratelimit/retrospective/
├── README.md                # ふりかえりの目的と書き方
├── template.md              # 質問 4 つの回答欄＋自由記述欄
└── examples/
    └── 2026-05-14_alice.md  # 過去受講者の回答例（匿名化）
```

`template.md` は git にコミットさせる前提で、受講者が `[氏名]_[日付].md` で複製して記入。蓄積された例が次の受講者の参考になる。

---

## T8. チュートリアル種類の不足【P3】

### 現状

- 教材は `ratelimit/`（中規模・標準フロー）の 1 種類のみ
- README.md の規模別フロー表に「小規模 / 大規模 / インフラ専業」の 3 区分があるのに対応教材なし

### 問題

- 小規模フロー（`0-C → 1 → 3 → 4`）の練習素材が無く、Step 0-A をスキップする判断練習ができない
- インフラ専業フロー（`0-C → 1 → 2 → [3→4]×N → 5-B`）の練習素材が無く、`terraform plan` を検証コマンドにする体験ができない

### 提案

優先度低めで、以下を追加候補に挙げる:

| 教材候補 | 規模 | 主スタック | 練習狙い |
|---|---|---|---|
| `tutorial/quick-bugfix/` | 小規模 | Python のみ | Step 0-A スキップ判断、軽量フロー |
| `tutorial/terraform-cloud-run/` | インフラ | Terraform / GCP | `terraform plan` の検証、Step 5-B のチェックリスト |
| `tutorial/ml-vertex/` | ML 系 | Vertex AI | Step 0-A / 0-B の重視、要件曖昧さの吸収 |

ratelimit 教材が安定運用に乗ってから着手すれば良い。

---

## T9. 細部【P3】

| 箇所 | 問題 | 修正 |
|---|---|---|
| [starter/README.md L20-24](../tutorial/ratelimit/starter/README.md#L20-L24) | `uv sync` のみ。テスト実行に必要な `--extra dev` が抜けている | `uv sync --extra dev` に修正 |
| [starter/src/myapi/services/user_cache.py L7-10](../tutorial/ratelimit/starter/src/myapi/services/user_cache.py#L7-L10) | `_FAKE_DB` がモジュールグローバル mutable。test 並列実行時に汚染リスク | `frozenset` か関数で返す形に変更、または `[ASSUMPTION]` でテスト独立性に依存しない旨を注記 |
| `client-brief/2026-05-14_ratelimit.md` | クライアント往復が単一メールのみ。実案件は複数往復ある | 「2 通目」を `client-brief/2026-05-15_clarification.md` として追加し、Step 0-A の `[QUESTION]` 後の回答を半分だけ返す（残り半分は意図的に曖昧）形にする |
| `solution/handoff-jsons/` のファイル名 | `phase1.json` 等で内容が読まないと判別できない | ディレクトリに `README.md` を追加し各 JSON の要点（key_decisions の例）を一覧化 |
| `tutorial/ratelimit/README.md` 全体 | 「進め方」がファシリ前提で書かれている | T1 で書き直し |

---

## 着手順序（提案）

1. **T4**（solution Phase 3 完成）— 教材として欠落箇所。最優先
2. **T3**（E2E 動作確認ハーネス）— 学習の報酬体験。受講者満足度に直結
3. **T1**（自学自習動線）— 利用者層拡大。マニュアル作業の負担減
4. **T2**（戻り先判定の難易度設計）+ **T5**（既存テスト強化）— 学習効果の質を上げる
5. **T6**（Makefile）+ **T7**（ふりかえり構造化）— 運用安定化
6. **T8**（教材種類拡張）— ratelimit が安定してから
7. **T9**（細部）— 並行して都度修正
