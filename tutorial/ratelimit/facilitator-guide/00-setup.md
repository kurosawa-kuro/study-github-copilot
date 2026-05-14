# 00. セットアップ

## 受講者環境

- Python 3.12（必須）
- uv または pip（uv 推奨）
- VS Code + GitHub Copilot 拡張
- Git（チェックポイントごとに commit する習慣付け）

## 事前手順

```bash
cd tutorial/ratelimit/starter
uv sync --extra dev
uv run pytest -q    # 既存テストが全パスすることを確認
```

すべてパスしたら準備完了。失敗した場合は受講者環境の問題なので先に潰す。

## ファシリ環境

- `solution/` に目を通しておくこと
- `facilitator-guide/01-step0a-expected-questions.md` で **受講者が出すべき `[QUESTION]` 一覧** を頭に入れる
- 進行の節目（Step 完了時）でラウンドテーブル

## 進行ルール

- **受講者は `solution/` を見ない**（事前にアナウンス）
- Copilot へのプロンプトは QUICK_GUIDE.md のテンプレを **そのまま** 貼って始める（独自アレンジは禁止）
- ファシリは `[QUESTION]` への回答だけ提供し、設計判断は教えない
- 各 Phase の Step 4 完了時、引き継ぎ JSON を Git にコミットさせる

## 時間配分（半日 × 2 構成の例）

**Day 1（午前 3h）**
- Step 0-A: 45 min
- Step 0-C: 15 min
- Step 1: 45 min
- Step 2: 60 min
- ふりかえり: 15 min

**Day 1（午後 4h）/ Day 2（午前 4h）**
- Phase 1 (Step 3 → 4): 1.5h
- Phase 2 (Step 3 → 4): 2h（戻り先判定が発生しがち）
- Phase 3 (Step 3 → 4): 1.5h
- Step 5-A: 45 min
- ふりかえり: 30 min
