#!/usr/bin/env bash
# PMTracker Full API Test Suite
# Covers all endpoints, auth controls, rate limiting, input validation,
# product deletion guard, all-four-metal prices, and JWT integrity.
#
# Usage:
#   ./test_api_full.sh [BASE_URL]
#   ./test_api_full.sh http://localhost:8000
#
# Requirements: curl, python3 (stdlib only)
# The script starts clean — it expects a FRESH backend instance with no
# password configured yet.

BASE="${1:-http://127.0.0.1:8000}"
FAILURES=0
TOKEN=""

pass() { printf '\033[0;32m[PASS]\033[0m %s\n' "$1"; }
fail() { printf '\033[0;31m[FAIL]\033[0m %s\n' "$1"; FAILURES=$((FAILURES+1)); }
info() { printf '\033[1;33m[INFO]\033[0m %s\n' "$1"; }

js()         { python3 -c "import sys,json; $1" 2>/dev/null; }
get_status() { curl -sL -o /dev/null -w "%{http_code}" "$@"; }
get_body()   { curl -sL "$@"; }
post_json()  { curl -sL -X POST  -H "Content-Type: application/json" "$@"; }
put_json()   { curl -sL -X PUT   -H "Content-Type: application/json" "$@"; }
delete_req() { curl -sL -X DELETE "$@"; }
auth()       { echo "Authorization: Bearer $TOKEN"; }

echo "══════════════════════════════════════════"
echo "  PMTracker Full API Test Suite"
echo "  $BASE"
echo "══════════════════════════════════════════"

# ─── 1. Public endpoints ───────────────────────────────────────────────────────
echo ""
echo "── 1. Public endpoints ──"

SC=$(get_status "$BASE/api/health")
[ "$SC" = "200" ] && pass "GET /api/health → 200" || fail "GET /api/health → $SC (expected 200)"

BODY=$(get_body "$BASE/")
echo "$BODY" | grep -q "Precious Metals" \
  && pass "GET / → API info present" \
  || fail "GET / → unexpected response: $BODY"

BODY=$(get_body "$BASE/api/auth/status")
echo "$BODY" | grep -q "password_configured" \
  && pass "GET /api/auth/status → field present" \
  || fail "GET /api/auth/status → $BODY"

# ─── 2. Auth setup & login ────────────────────────────────────────────────────
echo ""
echo "── 2. Auth setup & login ──"

SC=$(get_status -X POST "$BASE/api/auth/setup" -H "Content-Type: application/json" -d '{"password":"short"}')
[ "$SC" = "422" ] \
  && pass "Setup: password <8 chars → 422" \
  || fail "Setup: short password → $SC (expected 422)"

BODY=$(post_json "$BASE/api/auth/setup" -d '{"password":"testpass123"}')
TOKEN=$(js "d=json.load(sys.stdin); print(d.get('access_token',''))" <<< "$BODY")
[ -n "$TOKEN" ] \
  && pass "Setup: valid password → token issued" \
  || fail "Setup: no token → $BODY"

SC=$(get_status -X POST "$BASE/api/auth/setup" -H "Content-Type: application/json" -d '{"password":"testpass123"}')
[ "$SC" = "400" ] \
  && pass "Setup: duplicate attempt → 400" \
  || fail "Setup: duplicate → $SC (expected 400)"

SC=$(get_status -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" -d '{"password":"wrongpass1"}')
[ "$SC" = "401" ] \
  && pass "Login: wrong password → 401" \
  || fail "Login: wrong password → $SC (expected 401)"

SC=$(get_status -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" -d '{"password":"short"}')
[ "$SC" = "422" ] \
  && pass "Login: password <8 chars → 422" \
  || fail "Login: short password → $SC (expected 422)"

BODY=$(post_json "$BASE/api/auth/login" -d '{"password":"testpass123"}')
TOKEN=$(js "d=json.load(sys.stdin); print(d.get('access_token',''))" <<< "$BODY")
[ -n "$TOKEN" ] \
  && pass "Login: correct password → token issued" \
  || fail "Login: no token → $BODY"
info "TOKEN length: ${#TOKEN}"

# ─── 3. Rate limiting ─────────────────────────────────────────────────────────
echo ""
echo "── 3. Rate limiting ──"
info "Sending 10 failed login attempts (same IP)..."
for i in $(seq 1 10); do
  post_json "$BASE/api/auth/login" -d '{"password":"badpassword1"}' -o /dev/null
done
SC=$(get_status -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" -d '{"password":"badpassword1"}')
[ "$SC" = "429" ] \
  && pass "Rate limit: 11th attempt → 429 Too Many Requests" \
  || fail "Rate limit: expected 429 after 10 bad attempts, got $SC"

SC=$(get_status -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" -d '{"password":"testpass123"}')
[ "$SC" = "429" ] \
  && pass "Rate limit: correct password also blocked during window → 429" \
  || fail "Rate limit: expected 429 even for correct password, got $SC"

# ─── 4. Auth protection on all protected endpoints ───────────────────────────
echo ""
echo "── 4. Auth protection (no token) ──"
for EP in \
  "/api/metals/" \
  "/api/products/" \
  "/api/holdings/" \
  "/api/portfolio/summary" \
  "/api/portfolio/holdings" \
  "/api/portfolio/prices"; do
  SC=$(get_status "$BASE$EP")
  [ "$SC" = "401" ] \
    && pass "No token → $EP → 401" \
    || fail "No token → $EP → $SC (expected 401)"
done

# ─── 5. /api/admin/reseed protection ─────────────────────────────────────────
echo ""
echo "── 5. /api/admin/reseed ──"

SC=$(get_status -X POST "$BASE/api/admin/reseed")
[ "$SC" = "401" ] \
  && pass "Reseed without token → 401" \
  || fail "Reseed without token → $SC (expected 401)"

SC=$(get_status -X POST "$BASE/api/admin/reseed" -H "$(auth)")
[ "$SC" = "200" ] \
  && pass "Reseed with valid token → 200" \
  || fail "Reseed with valid token → $SC (expected 200)"

# ─── 6. Metals ────────────────────────────────────────────────────────────────
echo ""
echo "── 6. Metals ──"

BODY=$(get_body -H "$(auth)" "$BASE/api/metals/")
echo "$BODY" | grep -q "Gold" \
  && pass "GET /api/metals/ → Gold present" \
  || fail "GET /api/metals/ → $BODY"
COUNT=$(js "print(len(json.load(sys.stdin)))" <<< "$BODY")
[ "$COUNT" = "4" ] \
  && pass "GET /api/metals/ → 4 metals seeded" \
  || fail "GET /api/metals/ → expected 4, got '$COUNT'"

SC=$(get_status -X POST "$BASE/api/metals/" -H "$(auth)" -H "Content-Type: application/json" \
  -d '{"name":"Gold","symbol":"gold"}')
[ "$SC" = "409" ] \
  && pass "POST /api/metals/ duplicate → 409" \
  || fail "POST /api/metals/ duplicate → $SC (expected 409)"

SC=$(get_status -X POST "$BASE/api/metals/" -H "$(auth)" -H "Content-Type: application/json" \
  -d '{"name":"","symbol":"xx"}')
[ "$SC" = "422" ] \
  && pass "POST /api/metals/ empty name → 422" \
  || fail "POST /api/metals/ empty name → $SC (expected 422)"

# ─── 7. Products ──────────────────────────────────────────────────────────────
echo ""
echo "── 7. Products ──"

BODY=$(get_body -H "$(auth)" "$BASE/api/products/")
echo "$BODY" | grep -q "American Gold Eagle" \
  && pass "GET /api/products/ → seeded products present" \
  || fail "GET /api/products/ → $BODY"
COUNT=$(js "print(len(json.load(sys.stdin)))" <<< "$BODY")
info "Products seeded: $COUNT"

BODY=$(get_body -H "$(auth)" "$BASE/api/products/?metal_id=1")
echo "$BODY" | grep -q "Gold" \
  && pass "GET /api/products/?metal_id=1 → gold products returned" \
  || fail "GET /api/products/?metal_id=1 → $BODY"

# ─── 8. Holdings CRUD ─────────────────────────────────────────────────────────
echo ""
echo "── 8. Holdings CRUD ──"

BODY=$(post_json "$BASE/api/holdings/" -H "$(auth)" -d '{
  "product_id": 1,
  "quantity": 2,
  "purchase_date": "2024-01-15",
  "purchase_price_per_oz": 2000.00,
  "premium_paid": 50.00,
  "dealer": "ACME Metals",
  "storage_location": "Home Safe",
  "notes": "Test holding"
}')
HID=$(js "d=json.load(sys.stdin); print(d.get('id',''))" <<< "$BODY")
[ -n "$HID" ] \
  && pass "POST /api/holdings/ → created (id=$HID)" \
  || fail "POST /api/holdings/ → $BODY"

BODY=$(put_json "$BASE/api/holdings/$HID" -H "$(auth)" -d '{"quantity":5,"notes":"Updated"}')
js "d=json.load(sys.stdin); exit(0 if d.get('quantity')==5 else 1)" <<< "$BODY" \
  && pass "PUT /api/holdings/$HID → quantity updated to 5" \
  || fail "PUT /api/holdings/$HID → $BODY"

BODY=$(get_body -H "$(auth)" "$BASE/api/holdings/$HID")
echo "$BODY" | grep -q '"quantity":5' \
  && pass "GET /api/holdings/$HID → persisted update confirmed" \
  || fail "GET /api/holdings/$HID → $BODY"

BODY=$(delete_req "$BASE/api/holdings/$HID" -H "$(auth)")
echo "$BODY" | grep -qi "deleted" \
  && pass "DELETE /api/holdings/$HID → success" \
  || fail "DELETE /api/holdings/$HID → $BODY"

SC=$(get_status "$BASE/api/holdings/$HID" -H "$(auth)")
[ "$SC" = "404" ] \
  && pass "GET /api/holdings/$HID after delete → 404" \
  || fail "GET /api/holdings/$HID after delete → $SC (expected 404)"

# ─── 9. Product deletion — orphan guard ──────────────────────────────────────
echo ""
echo "── 9. Product deletion — orphan guard ──"

BODY=$(post_json "$BASE/api/holdings/" -H "$(auth)" -d '{
  "product_id": 1,
  "quantity": 1,
  "purchase_date": "2024-03-01",
  "purchase_price_per_oz": 1900.00
}')
HID2=$(js "d=json.load(sys.stdin); print(d.get('id',''))" <<< "$BODY")
[ -n "$HID2" ] \
  && pass "Setup: holding on product 1 created (id=$HID2)" \
  || fail "Setup: failed to create holding → $BODY"

SC=$(get_status -X DELETE "$BASE/api/products/1" -H "$(auth)")
[ "$SC" = "409" ] \
  && pass "DELETE /api/products/1 with active holdings → 409" \
  || fail "DELETE /api/products/1 with holdings → $SC (expected 409)"

# Clean up holding, then delete a custom (no-holding) product
delete_req "$BASE/api/holdings/$HID2" -H "$(auth)" -o /dev/null

BODY=$(post_json "$BASE/api/products/" -H "$(auth)" \
  -d '{"name":"Temp Test Bar","metal_id":1,"weight_oz":1.0}')
PID=$(js "d=json.load(sys.stdin); print(d.get('id',''))" <<< "$BODY")
if [ -n "$PID" ]; then
  SC=$(get_status -X DELETE "$BASE/api/products/$PID" -H "$(auth)")
  [ "$SC" = "200" ] \
    && pass "DELETE /api/products/$PID (no holdings) → 200" \
    || fail "DELETE /api/products/$PID (no holdings) → $SC (expected 200)"
fi

# ─── 10. Input validation ─────────────────────────────────────────────────────
echo ""
echo "── 10. Input validation ──"

SC=$(get_status -X POST "$BASE/api/holdings/" -H "$(auth)" -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":-1,"purchase_date":"2024-01-15","purchase_price_per_oz":2000}')
[ "$SC" = "422" ] && pass "Negative quantity → 422" || fail "Negative quantity → $SC (expected 422)"

SC=$(get_status -X POST "$BASE/api/holdings/" -H "$(auth)" -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":1,"purchase_date":"2099-12-31","purchase_price_per_oz":2000}')
[ "$SC" = "422" ] && pass "Future purchase date → 422" || fail "Future purchase date → $SC (expected 422)"

SC=$(get_status -X POST "$BASE/api/holdings/" -H "$(auth)" -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":1,"purchase_date":"2024-01-15","purchase_price_per_oz":-500}')
[ "$SC" = "422" ] && pass "Negative price → 422" || fail "Negative price → $SC (expected 422)"

SC=$(get_status -X POST "$BASE/api/holdings/" -H "$(auth)" -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":1,"purchase_date":"2024-01-15","purchase_price_per_oz":0}')
[ "$SC" = "422" ] && pass "Zero price → 422" || fail "Zero price → $SC (expected 422)"

SC=$(get_status -X POST "$BASE/api/holdings/" -H "$(auth)" -H "Content-Type: application/json" \
  -d '{"product_id":9999,"quantity":1,"purchase_date":"2024-01-15","purchase_price_per_oz":2000}')
[ "$SC" = "400" ] && pass "Non-existent product_id → 400" || fail "Non-existent product_id → $SC (expected 400)"

# ─── 11. Spot prices — all four metals ───────────────────────────────────────
echo ""
echo "── 11. Spot prices (all 4 metals) ──"

BODY=$(get_body -H "$(auth)" "$BASE/api/portfolio/prices")
for M in gold silver platinum palladium; do
  js "d=json.load(sys.stdin); exit(0 if '$M' in d and d['$M']>0 else 1)" <<< "$BODY" \
    && pass "Prices: $M present and > 0" \
    || fail "Prices: $M missing or zero → $BODY"
done
IS_FB=$(js "d=json.load(sys.stdin); print(d.get('is_fallback',''))" <<< "$BODY")
info "is_fallback=$IS_FB (True expected when no API key configured)"

# ─── 12. Portfolio summary & enriched holdings ───────────────────────────────
echo ""
echo "── 12. Portfolio endpoints ──"

post_json "$BASE/api/holdings/" -H "$(auth)" -o /dev/null -d '{
  "product_id": 1, "quantity": 2, "purchase_date": "2024-06-01",
  "purchase_price_per_oz": 2200.00, "premium_paid": 30.00
}'

BODY=$(get_body -H "$(auth)" "$BASE/api/portfolio/summary")
js "d=json.load(sys.stdin); exit(0 if all(k in d for k in ['total_cost','current_value','holdings_count','allocation_by_metal']) else 1)" <<< "$BODY" \
  && pass "GET /api/portfolio/summary → all expected fields present" \
  || fail "GET /api/portfolio/summary → $BODY"
js "d=json.load(sys.stdin); exit(0 if d['holdings_count']>0 else 1)" <<< "$BODY" \
  && pass "GET /api/portfolio/summary → holdings_count > 0" \
  || fail "GET /api/portfolio/summary → holdings_count=0"

BODY=$(get_body -H "$(auth)" "$BASE/api/portfolio/holdings")
js "d=json.load(sys.stdin); h=d[0]; exit(0 if all(k in h for k in ['current_value','profit_loss','total_weight_oz','current_spot_price','profit_loss_percent']) else 1)" <<< "$BODY" \
  && pass "GET /api/portfolio/holdings → all enriched fields present" \
  || fail "GET /api/portfolio/holdings → missing fields in $BODY"

# ─── 13. JWT integrity ────────────────────────────────────────────────────────
echo ""
echo "── 13. JWT integrity ──"

SC=$(get_status "$BASE/api/metals/" -H "Authorization: Bearer totallyinvalidtoken")
[ "$SC" = "401" ] && pass "Garbage token → 401" || fail "Garbage token → $SC (expected 401)"

SC=$(get_status "$BASE/api/metals/" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIiLCJleHAiOjk5OTk5OTk5OTl9.fakesig")
[ "$SC" = "401" ] && pass "Forged JWT (bad signature) → 401" || fail "Forged JWT → $SC (expected 401)"

SC=$(get_status "$BASE/api/metals/" -H "Authorization: ")
[ "$SC" = "401" ] && pass "Empty Authorization header → 401" || fail "Empty auth → $SC (expected 401)"

# ─── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
if [ "$FAILURES" -eq 0 ]; then
  printf '\033[0;32mAll tests passed.\033[0m\n'
else
  printf '\033[0;31m%d test(s) failed.\033[0m\n' "$FAILURES"
fi
echo "══════════════════════════════════════════"
exit "$FAILURES"
