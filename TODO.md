# PMTracker — Pending Improvements

This file tracks security and functionality improvements that are planned but not yet implemented.
Items are ordered by priority within each section.

---

## Security

### Medium Priority

#### S1: Switch JWT storage from `localStorage` to `httpOnly` cookies
**Files:** `frontend/src/services/api.js`, `frontend/src/contexts/AuthContext.jsx`, `backend/app/routes/auth.py`, `backend/app/auth.py`

`localStorage` is readable by any JavaScript on the page. An XSS vulnerability anywhere in the app would expose the token. Migrating to `httpOnly` cookies removes this risk entirely.

Required changes:
- Backend: set a `Set-Cookie: pmtracker_token=...; HttpOnly; SameSite=Strict; Path=/api` header on login/setup responses instead of returning the token in the body.
- Backend: add a `POST /api/auth/logout` endpoint that clears the cookie.
- Frontend: remove `localStorage` token reads/writes from `api.js` and `AuthContext.jsx`; rely on the browser sending the cookie automatically.
- Frontend: update `fetchJson()` to include `credentials: 'include'`.

---

#### S2: Implement token revocation / session invalidation
**Files:** `backend/app/auth.py`, `backend/app/models.py`

Currently there is no way to invalidate an issued JWT before it expires (24-hour window). Options:
- Store a `token_version` counter in `app_settings`. Embed the version in the JWT. Increment it on logout to invalidate all prior tokens.
- Maintain a small `revoked_tokens` table keyed by `jti` (JWT ID claim). Add a `jti` UUID to each token at creation time and check it on each request.

---

#### S3: Add `product_id` unique constraint on `(metal_id, name)` pair
**Files:** `backend/app/models.py`, `backend/app/migrate_db.py`

Duplicate product names within the same metal confuse the UI dropdown. Add a `UniqueConstraint('metal_id', 'name')` to the `Product` model and a corresponding `migrate_db.py` script to apply it to existing databases.

After adding the constraint, update `routes/products.py` `create_product` to catch `IntegrityError` and return HTTP 409 (same pattern now used in metals).

---

#### S4: Replace `alert()` / `window.confirm()` with inline UI feedback
**Files:** `frontend/src/App.jsx`

`alert()` and `confirm()` block the browser main thread and cannot be styled. Replace with:
- Inline error banners under the triggering form/button for mutation failures.
- A custom confirmation modal for the delete action.

---

#### S5: Add `Permissions-Policy` header to nginx
**File:** `frontend/nginx.conf`

Disable browser features the app does not use:

```nginx
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

---

### Lower Priority

#### S6: Audit logging for sensitive operations
**Files:** `backend/app/routes/auth.py`, `backend/app/routes/holdings.py`

Log auth events (login success/failure, setup) and destructive data operations (holding delete) to stdout with timestamp and client IP. FastAPI's built-in `logging` module is sufficient; no new dependency needed.

---

#### S7: Add `npm audit` to the build process
**File:** `frontend/package.json`

Add a `"preinstall": "npm audit --audit-level=high"` script so dependency vulnerabilities surface during Docker builds. Pair with periodic `npm audit fix` as part of maintenance.

---

## Functionality

### High Priority

#### F1: Add pagination to holdings endpoints
**Files:** `backend/app/routes/holdings.py`, `backend/app/routes/portfolio.py`

All holdings are fetched in a single query. For portfolios with hundreds of entries this will become slow. Add `skip: int = 0` and `limit: int = 100` query parameters to `GET /api/holdings` and `GET /api/portfolio/holdings`.

Frontend: add "Load more" or page-number controls to `HoldingsTable`.

---

#### F2: Product and metal management UI
**Files:** `frontend/src/App.jsx`, new `frontend/src/components/ProductsModal.jsx`

The backend already supports full CRUD for metals and products, but there is no frontend for it. Users must call the API directly to add custom bullion products.

Suggested approach: add a "Manage Products" link in the header that opens a modal listing existing products with a form to add new ones.

---

#### F3: Holdings filter and search
**File:** `frontend/src/components/HoldingsTable.jsx`

Add filter controls above the table:
- Dropdown: filter by metal type
- Date range pickers: from / to purchase date
- Text input: search by dealer or notes

All filtering can be done client-side on the already-fetched `holdings` array for small portfolios.

---

### Medium Priority

#### F4: Use `Decimal` for monetary calculations
**Files:** `backend/app/routes/portfolio.py`

Python `float` arithmetic accumulates rounding errors across many holdings. Replace `float` with `decimal.Decimal` for `total_cost`, `current_value`, and `profit_loss` calculations before rounding to two decimal places for the response.

---

#### F5: Debounce the "Refresh Prices" button
**File:** `frontend/src/App.jsx`

Rapid clicks on "Refresh Prices" fire multiple simultaneous API requests and can exhaust the external price API's rate limit. Add a short cooldown (e.g., 30 seconds) after a refresh before the button re-enables.

---

#### F6: Cache static data (products/metals) separately from live prices
**File:** `frontend/src/App.jsx`

`fetchData()` currently re-fetches products and metals on every refresh even though they rarely change. Separate the fetch into:
- `fetchStaticData()` — products, metals (called once on mount or after a mutation).
- `fetchLiveData()` — prices and portfolio summary (called on mount and on manual refresh).

---

#### F7: Show fallback price warning in the UI
**Files:** `frontend/src/App.jsx`, `backend/app/schemas.py`

`SpotPrices` already includes `is_fallback: bool`. When `true`, display a visible warning badge in the header ("Using approximate prices — live data unavailable") so users know their portfolio values may be stale.

---

### Lower Priority

#### F8: Modal keyboard accessibility
**File:** `frontend/src/components/AddHoldingModal.jsx`

- Close the modal when the user presses `Escape`.
- Add `aria-label="Close"` to the × button.
- Trap focus within the modal while it is open.

---

#### F9: SQLite absolute path in Docker
**File:** `docker-compose.yml`

The current `DATABASE_URL=sqlite:///./data/pmtracker.db` uses a path relative to the process working directory. If the working directory ever changes the app silently creates a second database. Change to an absolute path:

```yaml
DATABASE_URL=sqlite:////app/data/pmtracker.db
```

---

#### F10: Docker healthchecks and resource limits
**File:** `docker-compose.yml`

Add healthcheck definitions so Docker Compose can detect and restart unhealthy containers:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 30s
  timeout: 5s
  retries: 3
```

Add `mem_limit` and `cpus` constraints to prevent one container from starving the other.

---

#### F11: Consider PostgreSQL for production deployments
**Files:** `backend/app/database.py`, `docker-compose.yml`

SQLite is adequate for a single local user, but has limited write concurrency and a fragile backup story. Document or support an optional PostgreSQL configuration for users who want a more robust deployment.
