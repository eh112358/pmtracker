# PMTracker Test Plan

## Quick Start

1. **Fresh Start (recommended if experiencing issues):**
   ```bash
   # Delete old database
   rm backend/data/pmtracker.db

   # Rebuild containers
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Run API Tests:**
   - Windows: `powershell -ExecutionPolicy Bypass -File test_api.ps1`
   - Linux/Mac: `bash test_api.sh`

3. **Access the App:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 1. Backend API Tests

### 1.1 Health Check
- [ ] `GET /` - Returns API info
- [ ] `GET /api/health` - Returns healthy status

### 1.2 Authentication Endpoints
- [ ] `GET /api/auth/status` - Returns password_configured status
- [ ] `POST /api/auth/setup` - First-time password setup (min 8 chars)
- [ ] `POST /api/auth/setup` - Rejects if password already set
- [ ] `POST /api/auth/login` - Authenticates with correct password
- [ ] `POST /api/auth/login` - Rejects incorrect password
- [ ] Token expires after 24 hours

### 1.3 Protected Routes (require auth)
- [ ] All routes return 401 without valid token
- [ ] All routes work with valid Bearer token

### 1.4 Metals Endpoints
- [ ] `GET /api/metals` - Returns list of metals (gold, silver, platinum, palladium)

### 1.5 Products Endpoints
- [ ] `GET /api/products` - Returns all products
- [ ] `GET /api/products?metal_id=1` - Filters by metal

### 1.6 Holdings CRUD
- [ ] `GET /api/holdings` - Returns all holdings
- [ ] `POST /api/holdings` - Creates new holding
- [ ] `GET /api/holdings/{id}` - Returns specific holding
- [ ] `PUT /api/holdings/{id}` - Updates holding
- [ ] `DELETE /api/holdings/{id}` - Deletes holding

### 1.7 Portfolio Endpoints
- [ ] `GET /api/portfolio/prices` - Returns current spot prices
- [ ] `GET /api/portfolio/summary` - Returns portfolio summary
- [ ] `GET /api/portfolio/holdings` - Returns holdings with calculated values

### 1.8 Input Validation
- [ ] Quantity must be > 0 and <= 100,000
- [ ] Purchase price must be > 0 and <= 1,000,000
- [ ] Purchase date cannot be in the future
- [ ] Password must be >= 8 characters

## 2. Frontend Tests

### 2.1 Build Process
- [ ] Vite builds successfully without errors
- [ ] No critical deprecation warnings

### 2.2 Authentication UI
- [ ] Shows setup screen on first visit
- [ ] Password validation (min 8 chars, confirmation match)
- [ ] Shows login screen after password is set
- [ ] Logout clears token and returns to login
- [ ] Token persists in localStorage

### 2.3 Dashboard
- [ ] Displays spot prices in header
- [ ] Shows portfolio summary stats
- [ ] Refresh button updates prices

### 2.4 Holdings Management
- [ ] Add holding modal works
- [ ] Edit holding modal works
- [ ] Delete holding with confirmation
- [ ] Holdings table displays correctly

### 2.5 Allocation Chart
- [ ] Shows metal allocation percentages
- [ ] Updates when holdings change

## 3. Docker Tests

### 3.1 Container Security
- [ ] Backend runs as non-root user (appuser)
- [ ] Frontend runs as non-root user (nginx)
- [ ] Resource limits applied

### 3.2 Network
- [ ] Backend accessible on port 8000
- [ ] Frontend accessible on port 3000
- [ ] Frontend can proxy to backend

## 4. Integration Tests

### 4.1 Full Flow
- [ ] Fresh install shows password setup
- [ ] After setup, can login
- [ ] Can add a holding
- [ ] Portfolio values calculate correctly
- [ ] Can edit and delete holdings
- [ ] Logout and login again works
