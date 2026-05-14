#!/usr/bin/env bash
# Step 5-A 統合検証用 E2E シナリオ.
#
# 前提:
#   - 受講者の starter ツリーで Phase 1〜3 が完了している
#   - Redis が空 (compose.yaml で起動直後 / または FLUSHALL 済み)
#   - カレントディレクトリは tutorial/sales-aggregator/e2e/
#
# 使い方:
#   docker compose up -d         # Redis 起動
#   bash scenarios.sh            # 全シナリオ実行
#   docker compose down          # 後片付け
set -euo pipefail

STARTER_DIR="${STARTER_DIR:-../starter}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

INPUT_DAY1="$STARTER_DIR/data/input/sales_2026-05-14.csv"
INPUT_DAY2="$STARTER_DIR/data/input/sales_2026-05-15.csv"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "OK:   $*"; }

run_cli() {
    local out=$1; shift
    (cd "$STARTER_DIR" && uv run salesagg --output "$out" "$@") >/dev/null
}

# 状態をクリア
run_cli "$WORK/r0.csv" --input "$INPUT_DAY1" --reset >/dev/null

# ───────── シナリオ 1: 1 日目を取り込むと累積が当該分になる ─────────
# day1: p-001 (2+3=5 / 7500), p-002 (1+2=3 / 9600), p-003 (1 / 980)
out="$WORK/r1.csv"
run_cli "$out" --input "$INPUT_DAY1"
grep -q '^p-001,5,7500$' "$out" || fail "scenario 1: p-001 not 5/7500"
grep -q '^p-002,3,9600$' "$out" || fail "scenario 1: p-002 not 3/9600"
grep -q '^p-003,1,980$' "$out"  || fail "scenario 1: p-003 not 1/980"
ok "scenario 1: day1 imported correctly"

# ───────── シナリオ 2: 同じファイル再投入で値が変わらない (冪等) ─────────
out="$WORK/r2.csv"
run_cli "$out" --input "$INPUT_DAY1"
grep -q '^p-001,5,7500$' "$out" || fail "scenario 2: p-001 changed on re-ingest"
grep -q '^p-002,3,9600$' "$out" || fail "scenario 2: p-002 changed on re-ingest"
ok "scenario 2: re-ingest is idempotent"

# ───────── シナリオ 3: 2 日目で累積される ─────────
# day2: p-001 (+1 / +1500), p-003 (+4 / +3920), p-002 (+1 / +3200)
out="$WORK/r3.csv"
run_cli "$out" --input "$INPUT_DAY2"
grep -q '^p-001,6,9000$'   "$out" || fail "scenario 3: p-001 not 6/9000"
grep -q '^p-002,4,12800$'  "$out" || fail "scenario 3: p-002 not 4/12800"
grep -q '^p-003,5,4900$'   "$out" || fail "scenario 3: p-003 not 5/4900"
ok "scenario 3: day2 accumulates onto day1"

# ───────── シナリオ 4: --idempotency-key を変えれば再取り込みできる ─────────
# day1 を 2 回目取り込み: p-001 (6+5=11 / 16500)
out="$WORK/r4.csv"
run_cli "$out" --input "$INPUT_DAY1" --idempotency-key "reimport-1"
grep -q '^p-001,11,16500$' "$out" || fail "scenario 4: p-001 not 11/16500 (forced re-import failed)"
ok "scenario 4: explicit idempotency_key forces re-import"

# ───────── シナリオ 5: --reset 後は累積が消える ─────────
out="$WORK/r5.csv"
run_cli "$out" --input "$INPUT_DAY1" --reset
grep -q '^p-001,5,7500$' "$out" || fail "scenario 5: reset+import not clean"
[ "$(wc -l <"$out")" -eq 4 ] || fail "scenario 5: report has unexpected rows ($(wc -l <"$out"))"
ok "scenario 5: --reset clears cumulative and idempotency markers"

echo
echo "All scenarios passed."
