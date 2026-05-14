# tutorial/

QUICK_GUIDE.md の体系を一周する練習素材。

## 想定受講者

バックエンド専門ではなく、**Python スクリプト書き全般**。
主スタックは Python / Docker / CSV / Redis。

## 現状

| パス | 状態 |
|---|---|
| （新題材） | 準備中 |
| `_archive/ratelimit/` | アーカイブ。題材ミスマッチ（FastAPI / GCP 前提）のため退避 |

## 新題材を作るときの最小要件

- 題材は **Python / Docker / CSV / Redis** の範囲で完結すること（API / Web / クラウド固有サービスは入れない）
- 動線は **一本**（運用モードを増やさない）
- `client-brief/` `starter/` `solution/` `e2e/` の 4 ディレクトリ構成
- 全変更にテストコード必須
