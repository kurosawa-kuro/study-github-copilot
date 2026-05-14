#!/usr/bin/env bash
# Step 5-A 統合検証用 E2E シナリオ.
#
# 前提:
#   - myapi が http://localhost:8000 で起動済み
#   - MYAPI_RATELIMIT__LIMIT=5 / MYAPI_RATELIMIT__WINDOW_SECONDS=10 で起動
#   - Redis が空 (compose.yaml で redis を立ち上げ直後、または FLUSHALL 済み)
#
# 使い方:
#   bash scenarios.sh
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000}"
TOKEN_A="${TOKEN_A:-u-001}"
TOKEN_B="${TOKEN_B:-u-002}"
EXPECTED_LIMIT="${EXPECTED_LIMIT:-5}"
WINDOW_SECONDS="${WINDOW_SECONDS:-10}"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "OK:   $*"; }

# ───────── シナリオ 1: 上限内 (LIMIT 回) はすべて 200 ─────────
for i in $(seq 1 "$EXPECTED_LIMIT"); do
  code=$(curl -sS -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $TOKEN_A" "$BASE/users/u-001")
  [ "$code" = "200" ] || fail "scenario 1 iter=$i: expected 200, got $code"
done
ok "scenario 1: within limit returns 200 (×$EXPECTED_LIMIT)"

# ───────── シナリオ 2: LIMIT+1 回目は 429 + Retry-After ─────────
resp=$(curl -sS -i -H "Authorization: Bearer $TOKEN_A" "$BASE/users/u-001")
echo "$resp" | head -n 1 | grep -q "429" || fail "scenario 2: expected 429 status line"
echo "$resp" | grep -qi '^retry-after:' || fail "scenario 2: missing Retry-After header"
echo "$resp" | grep -qi '^x-ratelimit-remaining: 0' || fail "scenario 2: X-RateLimit-Remaining != 0"
ok "scenario 2: $((EXPECTED_LIMIT + 1))th request returns 429 with Retry-After"

# ───────── シナリオ 3: /health はレートリミット対象外 ─────────
for i in $(seq 1 50); do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE/health")
  [ "$code" = "200" ] || fail "scenario 3 iter=$i: expected 200, got $code"
done
ok "scenario 3: /health is not rate-limited (×50)"

# ───────── シナリオ 4: 別ユーザーは独立カウンタ ─────────
code=$(curl -sS -o /dev/null -w '%{http_code}' \
  -H "Authorization: Bearer $TOKEN_B" "$BASE/users/u-002")
[ "$code" = "200" ] || fail "scenario 4: expected 200 for fresh user, got $code"
ok "scenario 4: separate user_id has independent counter"

# ───────── シナリオ 5: 認証なしは 401 (カウンタ非消費) ─────────
code=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE/users/u-001")
[ "$code" = "401" ] || fail "scenario 5: expected 401, got $code"
ok "scenario 5: unauthenticated returns 401"

# ───────── シナリオ 6: 窓リセット後に再度通る ─────────
echo "      waiting ${WINDOW_SECONDS}s for window reset..."
sleep "$WINDOW_SECONDS"
code=$(curl -sS -o /dev/null -w '%{http_code}' \
  -H "Authorization: Bearer $TOKEN_A" "$BASE/users/u-001")
[ "$code" = "200" ] || fail "scenario 6: expected 200 after window reset, got $code"
ok "scenario 6: window reset releases the limit"

echo
echo "All scenarios passed."
