# study-github-copilot

GitHub Copilot を「上流から下流まで」抜けなく使い倒すための **プロンプトテンプレート** と
**ハンズオン教材** をまとめたリポジトリ。

---

## プロジェクト目的

> Copilot に「曖昧な依頼を曖昧なまま実装させない」体系を提供する。

実装フェーズだけの「調査 → 計画 → 実装 → レビュー」では、上流（要件・設計）と下流（統合・デプロイ）が抜け落ちる。
本リポジトリは Step 0 系（要件明確化・前提固定）と Step 5 系（統合検証・デプロイ準備）、および
Step 4 への **戻り先判定ループ** を加えた v3 体系を提供する。

主な提供物:

1. **プロンプトテンプレ本体**（`docs/QUICK_GUIDE.md` / `docs/PROMPT_TEMPLATE.md`） — Step 0-A〜5-C のコピペ可能なテンプレ
2. **完成済みハンズオン**（`tutorial/ratelimit/`） — 中規模チュートリアル一式

対象スタック: Python / Redis / Terraform / GCP

---

## 使い方

### A. 実案件で使う

1. [docs/QUICK_GUIDE.md の規模別フロー早見表](docs/QUICK_GUIDE.md#規模別フロー) で案件規模を判定（小規模 / 標準 / 大規模 / インフラ専業）
2. フローの順に `QUICK_GUIDE.md` の該当 Step プロンプトを **そのまま Copilot に貼る**
3. `[...]` を実内容に、`{N}` を Phase 番号に置換
4. 出力に `[ASSUMPTION]` / `[QUESTION]` / `[AMBIGUITY]` / `[BREAKING]` 等のタグが付いていることを確認
   - **タグなしの推測・決定は不完全とみなして再実行**
5. Step 4 で問題が出たら **戻り先判定表** に従って該当 Step に戻る

### B. チュートリアルで練習する

1. `tutorial/` 配下の完成済み教材を使う（現状 `tutorial/ratelimit/` = 中規模・標準フロー一周）
2. 教材 README に従い `starter/` を修正していく
3. 行き詰まったら `facilitator-guide/` を見る（ファシリ用なので最後の手段）

### C. QUICK_GUIDE.md の活用ポイント

| シーン | 使う節 |
|---|---|
| 案件が来た瞬間 | 「規模別フロー」で規模判定 → 該当 Step だけ抜き出す |
| 依頼が曖昧 | Step 0-A をまず貼る → `[QUESTION]` が全部消えてから次へ |
| 既存コードに触る | Step 0-C で前提固定（特に Redis キー規約・後方互換性） |
| Phase 実装中 | Step 0-C を **Phase 毎に再貼り付け**（コンテキスト落ち対策） |
| Step 4 で × が出た | 「戻り先」表を見て Step 0-A〜3 のどこに戻すか判定 |
| 本番投入直前 | Step 5-B のチェックリストを 1 項目ずつ潰す |

---

## 工程全体マップ

```
[上流: Step 0 系]                [実装本体: Step 1-4]                [下流: Step 5 系]
─────────────────              ────────────────────              ─────────────────
0-A 要件明確化      ──▶  1 調査 ──▶ 2 計画 ──▶ 3 実装 ──▶ 4 レビュー  ──▶  5-A 統合検証
0-B 設計判断（保留）            ▲                          │                  5-B デプロイ準備
0-C 前提固定                    └─────── ループ戻り ◀──────┘                  5-C 振り返り（保留）
```

- **上流**: 案件開始時に 1 回
- **実装本体**: Phase ごとに Step 3 → 4 を繰り返し
- **下流**: 実装完了後に 1 回

詳細・全プロンプト本文は [docs/QUICK_GUIDE.md](docs/QUICK_GUIDE.md) を参照。

---

## ディレクトリ構成

```
study-github-copilot/
├── README.md                       本書 — プロジェクト全体ナビ
├── docs/
│   ├── QUICK_GUIDE.md              ★メイン: 圧縮版テンプレ + 規模別フロー + タグ + 戻り先判定
│   └── PROMPT_TEMPLATE.md          v3 設計仕様 + Step 0-A〜5-C プロンプト本文
└── tutorial/
    └── ratelimit/                  完成済み中規模チュートリアル（標準フロー一周）
        ├── README.md               チュートリアル概要・進め方
        ├── client-brief/           クライアントから届いた依頼書（意図的に薄い）
        ├── starter/                受講者が修正していくベースコード（FastAPI + Redis）
        ├── solution/               模範解答（Phase ごと + 引き継ぎ JSON 見本）
        └── facilitator-guide/      ファシリ用ガイド + ルーブリック
```

---

## ドキュメント一覧

| パス | 役割 | いつ読む |
|---|---|---|
| [README.md](README.md) | プロジェクト全体ナビ・目的・使い方 | 最初 |
| [docs/QUICK_GUIDE.md](docs/QUICK_GUIDE.md) | 圧縮版プロンプトテンプレ・規模別フロー・タグ一覧・戻り先判定表 | 実案件で Copilot に貼る都度 |
| [docs/PROMPT_TEMPLATE.md](docs/PROMPT_TEMPLATE.md) | v3 設計仕様（背景・工程全体マップ・運用上の留意点）+ Step 0-A〜5-C プロンプト本文 | 体系を理解するとき・新メンバー導入時 |
| [tutorial/ratelimit/README.md](tutorial/ratelimit/README.md) | 中規模ハンズオン: API レートリミット導入 | 標準フローを一周したいとき |
| [tutorial/ratelimit/facilitator-guide/99-rubric.md](tutorial/ratelimit/facilitator-guide/99-rubric.md) | チュートリアル評価ルーブリック | ファシリ・自己評価時 |

---

## 段階導入ガイド・領域別適用差

無理に全 Step を一度に入れる必要はない。即時導入推奨は **Step 0-C 前提固定** と **タグ運用**、戻り先判定の 3 つ。詳細は [docs/PROMPT_TEMPLATE.md の段階導入ガイド](docs/PROMPT_TEMPLATE.md#段階導入ガイド) と [領域別の適用差](docs/PROMPT_TEMPLATE.md#領域別の適用差) を参照（単一正本）。

---

## 改訂履歴

[docs/PROMPT_TEMPLATE.md の改訂履歴](docs/PROMPT_TEMPLATE.md#改訂履歴) を参照（単一正本）。
