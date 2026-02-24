# PMTracker API Test Script (PowerShell)
# Run this after starting the Docker containers

$BASE_URL = "http://localhost:8000"
$TOKEN = ""

Write-Host "======================================"
Write-Host "PMTracker API Test Suite"
Write-Host "======================================"
Write-Host ""

function Pass($msg) { Write-Host "[PASS] $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red }
function Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Yellow }

# Test 1: Health check
Write-Host "1. Testing Health Endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/health" -Method Get
    if ($response.status -eq "healthy") {
        Pass "Health check passed"
    } else {
        Fail "Health check unexpected response"
    }
} catch {
    Fail "Health check failed: $_"
}

# Test 2: Root endpoint
Write-Host ""
Write-Host "2. Testing Root Endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
    if ($response.message -like "*Precious Metals*") {
        Pass "Root endpoint returns API info"
    } else {
        Fail "Root endpoint unexpected response"
    }
} catch {
    Fail "Root endpoint failed: $_"
}

# Test 3: Auth status
Write-Host ""
Write-Host "3. Testing Auth Status..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/auth/status" -Method Get
    Pass "Auth status endpoint works"
    if ($response.password_configured) {
        Info "Password is already configured"
    } else {
        Info "Password not yet configured (first-time setup needed)"
    }
    $passwordConfigured = $response.password_configured
} catch {
    Fail "Auth status failed: $_"
    $passwordConfigured = $null
}

# Test 4: Setup or Login
Write-Host ""
if ($passwordConfigured -eq $false) {
    Write-Host "4. Testing Password Setup..."
    try {
        $body = @{ password = "testpass123" } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/auth/setup" -Method Post -Body $body -ContentType "application/json"
        if ($response.access_token) {
            Pass "Password setup successful"
            $TOKEN = $response.access_token
        } else {
            Fail "Password setup failed"
        }
    } catch {
        Fail "Password setup failed: $_"
    }
} else {
    Write-Host "4. Testing Login..."
    try {
        $body = @{ password = "testpass123" } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $body -ContentType "application/json"
        if ($response.access_token) {
            Pass "Login successful"
            $TOKEN = $response.access_token
        }
    } catch {
        Info "Login with 'testpass123' failed, prompting for password..."
        $securePassword = Read-Host "Enter password" -AsSecureString
        $password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
        try {
            $body = @{ password = $password } | ConvertTo-Json
            $response = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $body -ContentType "application/json"
            if ($response.access_token) {
                Pass "Login successful"
                $TOKEN = $response.access_token
            }
        } catch {
            Fail "Login failed: $_"
        }
    }
}

if (-not $TOKEN) {
    Fail "No token obtained, cannot continue authenticated tests"
    exit 1
}

$headers = @{ Authorization = "Bearer $TOKEN" }

# Test 5: Protected route without auth
Write-Host ""
Write-Host "5. Testing Protected Routes (without auth)..."
try {
    $null = Invoke-RestMethod -Uri "$BASE_URL/api/holdings" -Method Get
    Fail "Holdings endpoint should return 401 without auth"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Pass "Holdings endpoint returns 401 without auth"
    } else {
        Fail "Unexpected error: $_"
    }
}

# Test 6: Get Metals
Write-Host ""
Write-Host "6. Testing Metals Endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/metals" -Method Get -Headers $headers
    if ($response.Count -gt 0) {
        Pass "Metals endpoint returns data"
        Info "Found $($response.Count) metals"
    } else {
        Fail "No metals found"
    }
} catch {
    Fail "Metals endpoint failed: $_"
}

# Test 7: Get Products
Write-Host ""
Write-Host "7. Testing Products Endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/products" -Method Get -Headers $headers
    if ($response.Count -gt 0) {
        Pass "Products endpoint returns data"
        Info "Found $($response.Count) products"
    } else {
        Fail "No products found"
    }
} catch {
    Fail "Products endpoint failed: $_"
}

# Test 8: Get Holdings
Write-Host ""
Write-Host "8. Testing Holdings Endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/holdings" -Method Get -Headers $headers
    Pass "Holdings endpoint works"
    Info "Found $($response.Count) holdings"
} catch {
    Fail "Holdings endpoint failed: $_"
}

# Test 9: Get Spot Prices
Write-Host ""
Write-Host "9. Testing Spot Prices..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/portfolio/prices" -Method Get -Headers $headers
    if ($response.gold -gt 0) {
        Pass "Prices endpoint works"
        Info "Gold: `$$($response.gold), Silver: `$$($response.silver)"
    } else {
        Fail "Invalid prices"
    }
} catch {
    Fail "Prices endpoint failed: $_"
}

# Test 10: Portfolio Summary
Write-Host ""
Write-Host "10. Testing Portfolio Summary..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/portfolio/summary" -Method Get -Headers $headers
    if ($null -ne $response.total_cost) {
        Pass "Portfolio summary works"
    } else {
        Fail "Portfolio summary invalid"
    }
} catch {
    Fail "Portfolio summary failed: $_"
}

# Test 11: Create holding
Write-Host ""
Write-Host "11. Testing Create Holding..."
try {
    $body = @{
        product_id = 1
        quantity = 2
        purchase_date = "2024-01-15"
        purchase_price_per_oz = 2000.00
        premium_paid = 50.00
        dealer = "Test Dealer"
        storage_location = "Home Safe"
        notes = "Test holding"
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/holdings" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    if ($response.id) {
        Pass "Create holding successful"
        Info "Created holding ID: $($response.id)"
        $holdingId = $response.id
    } else {
        Fail "Create holding failed"
        $holdingId = $null
    }
} catch {
    Fail "Create holding failed: $_"
    $holdingId = $null
}

# Test 12: Update holding
if ($holdingId) {
    Write-Host ""
    Write-Host "12. Testing Update Holding..."
    try {
        $body = @{ quantity = 3; notes = "Updated test holding" } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/holdings/$holdingId" -Method Put -Headers $headers -Body $body -ContentType "application/json"
        if ($response.quantity -eq 3) {
            Pass "Update holding successful"
        } else {
            Fail "Update holding failed"
        }
    } catch {
        Fail "Update holding failed: $_"
    }

    # Test 13: Delete holding
    Write-Host ""
    Write-Host "13. Testing Delete Holding..."
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/holdings/$holdingId" -Method Delete -Headers $headers
        if ($response.message -like "*deleted*") {
            Pass "Delete holding successful"
        } else {
            Fail "Delete holding failed"
        }
    } catch {
        Fail "Delete holding failed: $_"
    }
}

# Test 14: Input validation
Write-Host ""
Write-Host "14. Testing Input Validation (negative quantity)..."
try {
    $body = @{
        product_id = 1
        quantity = -1
        purchase_date = "2024-01-15"
        purchase_price_per_oz = 2000.00
    } | ConvertTo-Json
    $null = Invoke-RestMethod -Uri "$BASE_URL/api/holdings" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Fail "Negative quantity should be rejected"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 422) {
        Pass "Negative quantity rejected (422)"
    } else {
        Pass "Negative quantity rejected"
    }
}

Write-Host ""
Write-Host "15. Testing Input Validation (future date)..."
try {
    $futureDate = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
    $body = @{
        product_id = 1
        quantity = 1
        purchase_date = $futureDate
        purchase_price_per_oz = 2000.00
    } | ConvertTo-Json
    $null = Invoke-RestMethod -Uri "$BASE_URL/api/holdings" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Fail "Future date should be rejected"
} catch {
    Pass "Future date rejected"
}

Write-Host ""
Write-Host "======================================"
Write-Host "Test Suite Complete"
Write-Host "======================================"
