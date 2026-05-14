# 02. Step 0-C 前提固定

QUICK_GUIDE.md の Step 0-C テンプレを受講者に貼らせる。
本チュートリアル固有で **必ず固定すべき** 値は以下。

## 固定値

| 項目 | 値 |
|---|---|
| アプリ言語 | Python 3.12 |
| フレームワーク | FastAPI |
| Redis クライアント | redis-py |
| テスト | pytest + **fakeredis**（testcontainers ではない） |
| 依存管理 | uv |
| IaC | Terraform（**今回は変更しない**） |
| Redis キー規約 | `app:<feature>:<id>` |
| 認証方式 | Bearer トークン（既存 middleware で処理済み） |
| 後方互換性 | **必須**（既存 `/users`, `/orders`, `/health` の挙動を変えない） |

## 受講者の典型ミス

| ミス | 指摘ポイント |
|---|---|
| `slowapi` などサードパーティ採用を提案 | 依頼書「FastAPI のミドルウェアで」と既存スタック制約に反する |
| testcontainers-redis を使い始める | `CONVENTIONS.md` で fakeredis 採用と明記 |
| Terraform 変更を Phase に含める | 「IaC は変更しない」前提を Step 0-C で固定したはず |
| 監視・アラート設計を始める | Step 0-A で Non-Goal にした（別チケット） |

## 期待アウトプット

受講者は最後に「**前提固定完了**」と出力する。
ファシリは上の固定値が全て含まれているかをざっと確認。
