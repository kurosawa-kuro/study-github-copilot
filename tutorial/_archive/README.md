# tutorial/_archive/

題材が現在の方針と噛み合わない過去教材の退避場所。削除はしないが、新規受講者には案内しない。

## 一覧

| 項目 | 退避理由 |
|---|---|
| `ratelimit/` | FastAPI middleware / HTTP 仕様 / GCP に依存する判断が中核。現スコープ（Python / Docker / CSV / Redis）外 |
| `REFACTORING.md` | `ratelimit/` 教材時代のドキュメント体系リファクタ案メモ。歴史記録として保持 |
| `REFACTORING_TUTORIAL.md` | `ratelimit/` 教材時代の教材リファクタ案メモ。歴史記録として保持 |

## 注意

`ratelimit/` の内部構造（モード A/B 併存・self-review・E2E ハーネス・S/A/B/C ルーブリック等）は **過剰**。
新題材ではこれらの仕様を踏襲せず、単一動線でシンプルに作る（[../README.md](../README.md) 参照）。
