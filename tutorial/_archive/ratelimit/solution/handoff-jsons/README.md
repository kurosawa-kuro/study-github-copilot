# handoff-jsons/

各 Phase の Step 4 完了時に出す「引き継ぎ JSON」のサンプル。

## ファイル一覧

| ファイル | 主な key_decisions | 主な breaking_changes |
|---|---|---|
| `phase1.json` | 汎用 KV を Protocol で定義、UserCacheRedis は委譲化 | なし |
| `phase2.json` | 固定窓 INCR + 初回 EXPIRE / X-Forwarded-For 先頭で IP 識別 | `/orders` ゲートウェイ 600/min と二重制御 |
| `phase3.json` | RatelimitSettings を Settings 入れ子で追加 / X-RateLimit-* ヘッダ整備 | なし |

## 使い方

- 受講者は **Phase N の Step 4 完了時** に同形式の JSON を出力する
- ファシリは Phase N+1 開始時、受講者の引き継ぎ JSON を受け取り Phase N+1 Step 3 の入力にする
- Step 5-A では 3 つの引き継ぎ JSON を時系列で並べて整合性を検証

## 形式

QUICK_GUIDE.md Step 4 の「Phase 間引き継ぎ」セクション参照。
