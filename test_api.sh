#!/bin/bash
# PMTracker API Test Script
# Run this after starting the Docker containers

BASE_URL="http://localhost:8000"
TOKEN=""

echo "======================================"
echo "PMTracker API Test Suite"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }
info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# Test 1: Health check
echo "1. Testing Health Endpoint..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health")
if [ "$RESPONSE" = "200" ]; then
    pass "Health check returned 200"
else
    fail "Health check failed (HTTP $RESPONSE)"
fi

# Test 2: Root endpoint
echo ""
echo "2. Testing Root Endpoint..."
RESPONSE=$(curl -s "$BASE_URL/")
if echo "$RESPONSE" | grep -q "Precious Metals Tracker API"; then
    pass "Root endpoint returns API info"
else
    fail "Root endpoint unexpected response"
fi

# Test 3: Auth status
echo ""
echo "3. Testing Auth Status..."
RESPONSE=$(curl -s "$BASE_URL/api/auth/status")
if echo "$RESPONSE" | grep -q "password_configured"; then
    pass "Auth status endpoint works"
    if echo "$RESPONSE" | grep -q "true"; then
        info "Password is already configured"
    else
        info "Password not yet configured (first-time setup needed)"
    fi
else
    fail "Auth status failed"
fi

# Test 4: Check if password needs setup
PASSWORD_CONFIGURED=$(curl -s "$BASE_URL/api/auth/status" | grep -o '"password_configured":[^,}]*' | cut -d':' -f2)

if [ "$PASSWORD_CONFIGURED" = "false" ]; then
    echo ""
    echo "4. Testing Password Setup..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/setup" \
        -H "Content-Type: application/json" \
        -d '{"password":"testpass123"}')
    if echo "$RESPONSE" | grep -q "access_token"; then
        pass "Password setup successful"
        TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    else
        fail "Password setup failed: $RESPONSE"
    fi
else
    echo ""
    echo "4. Testing Login..."
    info "Skipping setup, attempting login with 'testpass123'"
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"password":"testpass123"}')
    if echo "$RESPONSE" | grep -q "access_token"; then
        pass "Login successful"
        TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    else
        fail "Login failed (may need correct password): $RESPONSE"
        echo ""
        echo "Enter password to continue tests (or Ctrl+C to skip):"
        read -s USER_PASSWORD
        RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
            -H "Content-Type: application/json" \
            -d "{\"password\":\"$USER_PASSWORD\"}")
        if echo "$RESPONSE" | grep -q "access_token"; then
            pass "Login successful with provided password"
            TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        else
            fail "Login failed"
        fi
    fi
fi

if [ -z "$TOKEN" ]; then
    fail "No token obtained, cannot continue authenticated tests"
    exit 1
fi

# Test 5: Protected route without auth
echo ""
echo "5. Testing Protected Routes (without auth)..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/holdings")
if [ "$RESPONSE" = "401" ]; then
    pass "Holdings endpoint returns 401 without auth"
else
    fail "Holdings endpoint should return 401 without auth (got $RESPONSE)"
fi

# Test 6: Get Metals
echo ""
echo "6. Testing Metals Endpoint..."
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/metals")
if echo "$RESPONSE" | grep -q "Gold"; then
    pass "Metals endpoint returns data"
    METAL_COUNT=$(echo "$RESPONSE" | grep -o '"id":' | wc -l)
    info "Found $METAL_COUNT metals"
else
    fail "Metals endpoint failed: $RESPONSE"
fi

# Test 7: Get Products
echo ""
echo "7. Testing Products Endpoint..."
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/products")
if echo "$RESPONSE" | grep -q "American Gold Eagle"; then
    pass "Products endpoint returns data"
    PRODUCT_COUNT=$(echo "$RESPONSE" | grep -o '"id":' | wc -l)
    info "Found $PRODUCT_COUNT products"
else
    fail "Products endpoint failed: $RESPONSE"
fi

# Test 8: Get Holdings
echo ""
echo "8. Testing Holdings Endpoint..."
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/holdings")
if [ "$RESPONSE" = "[]" ] || echo "$RESPONSE" | grep -q '"id":'; then
    pass "Holdings endpoint works"
    HOLDING_COUNT=$(echo "$RESPONSE" | grep -o '"id":' | wc -l)
    info "Found $HOLDING_COUNT holdings"
else
    fail "Holdings endpoint failed: $RESPONSE"
fi

# Test 9: Get Spot Prices
echo ""
echo "9. Testing Spot Prices..."
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/portfolio/prices")
if echo "$RESPONSE" | grep -q '"gold":'; then
    pass "Prices endpoint works"
    GOLD=$(echo "$RESPONSE" | grep -o '"gold":[0-9.]*' | cut -d':' -f2)
    SILVER=$(echo "$RESPONSE" | grep -o '"silver":[0-9.]*' | cut -d':' -f2)
    info "Gold: \$$GOLD, Silver: \$$SILVER"
else
    fail "Prices endpoint failed: $RESPONSE"
fi

# Test 10: Get Portfolio Summary
echo ""
echo "10. Testing Portfolio Summary..."
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/portfolio/summary")
if echo "$RESPONSE" | grep -q "total_cost"; then
    pass "Portfolio summary works"
else
    fail "Portfolio summary failed: $RESPONSE"
fi

# Test 11: Create a holding
echo ""
echo "11. Testing Create Holding..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/holdings" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "product_id": 1,
        "quantity": 2,
        "purchase_date": "2024-01-15",
        "purchase_price_per_oz": 2000.00,
        "premium_paid": 50.00,
        "dealer": "Test Dealer",
        "storage_location": "Home Safe",
        "notes": "Test holding"
    }')
if echo "$RESPONSE" | grep -q '"id":'; then
    pass "Create holding successful"
    HOLDING_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    info "Created holding ID: $HOLDING_ID"
else
    fail "Create holding failed: $RESPONSE"
    HOLDING_ID=""
fi

# Test 12: Update the holding
if [ -n "$HOLDING_ID" ]; then
    echo ""
    echo "12. Testing Update Holding..."
    RESPONSE=$(curl -s -X PUT "$BASE_URL/api/holdings/$HOLDING_ID" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"quantity": 3, "notes": "Updated test holding"}')
    if echo "$RESPONSE" | grep -q '"quantity":3'; then
        pass "Update holding successful"
    else
        fail "Update holding failed: $RESPONSE"
    fi

    # Test 13: Delete the holding
    echo ""
    echo "13. Testing Delete Holding..."
    RESPONSE=$(curl -s -X DELETE "$BASE_URL/api/holdings/$HOLDING_ID" \
        -H "Authorization: Bearer $TOKEN")
    if echo "$RESPONSE" | grep -q "deleted"; then
        pass "Delete holding successful"
    else
        fail "Delete holding failed: $RESPONSE"
    fi
fi

# Test 14: Input validation
echo ""
echo "14. Testing Input Validation..."

# Test negative quantity
RESPONSE=$(curl -s -X POST "$BASE_URL/api/holdings" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "product_id": 1,
        "quantity": -1,
        "purchase_date": "2024-01-15",
        "purchase_price_per_oz": 2000.00
    }')
if echo "$RESPONSE" | grep -qi "validation\|greater than"; then
    pass "Negative quantity rejected"
else
    fail "Negative quantity should be rejected: $RESPONSE"
fi

# Test future date
FUTURE_DATE=$(date -d "+30 days" +%Y-%m-%d 2>/dev/null || date -v+30d +%Y-%m-%d 2>/dev/null || echo "2099-12-31")
RESPONSE=$(curl -s -X POST "$BASE_URL/api/holdings" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"product_id\": 1,
        \"quantity\": 1,
        \"purchase_date\": \"$FUTURE_DATE\",
        \"purchase_price_per_oz\": 2000.00
    }")
if echo "$RESPONSE" | grep -qi "future\|validation"; then
    pass "Future date rejected"
else
    fail "Future date should be rejected: $RESPONSE"
fi

# Test short password
echo ""
echo "15. Testing Password Validation..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/setup" \
    -H "Content-Type: application/json" \
    -d '{"password":"short"}')
if echo "$RESPONSE" | grep -qi "8 char\|validation\|already"; then
    pass "Short password rejected (or password already set)"
else
    fail "Short password should be rejected: $RESPONSE"
fi

echo ""
echo "======================================"
echo "Test Suite Complete"
echo "======================================"
