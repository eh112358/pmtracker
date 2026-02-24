# CLAUDE.md — PMTracker Codebase Guide

This file provides orientation for AI assistants working on this repository. It covers architecture, conventions, development workflows, and key patterns.

---

## Project Overview

**PMTracker** is a self-hosted precious metals portfolio tracker. It is a full-stack web application composed of:

- A **Python/FastAPI** backend with SQLite storage
- A **React/Vite** frontend served via Nginx
- **Docker Compose** for local and production deployment

The app allows a single user (password-protected, no multi-user support) to track physical holdings of Gold, Silver, Platinum, and Palladium with live spot price integration.

---

## Repository Structure

```
pmtracker/
├── CLAUDE.md                  # This file
├── README.md                  # User-facing documentation
├── TEST_PLAN.md               # Manual testing checklist
├── docker-compose.yml         # Multi-container deployment
├── .env.example               # Environment variable template
├── test_api.sh                # Bash API integration tests
├── test_api.ps1               # PowerShell API integration tests
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt       # Python dependencies (pinned)
│   ├── data/                  # SQLite DB lives here (volume-mounted)
│   └── app/
│       ├── main.py            # FastAPI app entry point, startup seeding
│       ├── auth.py            # Password hashing, JWT creation, auth dependency
│       ├── database.py        # SQLAlchemy engine, session factory, Base
│       ├── models.py          # ORM models (Metal, Product, Holding, AppSettings)
│       ├── schemas.py         # Pydantic request/response schemas + validators
│       ├── migrate_db.py      # Ad-hoc migration utility
│       ├── routes/
│       │   ├── auth.py        # /api/auth/* endpoints
│       │   ├── metals.py      # /api/metals/* endpoints
│       │   ├── products.py    # /api/products/* endpoints
│       │   ├── holdings.py    # /api/holdings/* endpoints
│       │   └── portfolio.py   # /api/portfolio/* endpoints
│       └── services/
│           └── price_service.py  # External spot price fetching with caching
└── frontend/
    ├── Dockerfile
    ├── package.json           # Node dependencies (React 18, Vite 6)
    ├── vite.config.js         # Dev server (port 3000), proxy to :8000, dist output
    ├── index.html
    ├── nginx.conf             # Production nginx (port 8080, security headers, SPA routing)
    └── src/
        ├── main.jsx           # React entry point
        ├── App.jsx            # Root component, data fetching, layout
        ├── index.css          # Global styles
        ├── components/
        │   ├── Login.jsx          # Setup (first-time) and Login modes
        │   ├── Dashboard.jsx      # Stat cards (cost, value, P/L, return, count)
        │   ├── HoldingsTable.jsx  # Holdings list with edit/delete
        │   ├── AddHoldingModal.jsx # Add/edit form modal
        │   └── AllocationChart.jsx # Horizontal bar chart by metal
        ├── contexts/
        │   └── AuthContext.jsx    # Auth state, token management, setup/login/logout
        └── services/
            └── api.js             # Centralized API client, Bearer token injection
```

---

## Development Setup

### Running with Docker (recommended)

```bash
# Copy and configure environment
cp .env.example .env

# Start both services
docker-compose up --build

# Backend API:  http://localhost:8000
# Frontend UI:  http://localhost:3000
# API docs:     http://localhost:8000/docs
```

### Running Without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start                       # Dev server on http://localhost:3000
```

The Vite dev server proxies all `/api/*` requests to `http://localhost:8000`, so no separate CORS configuration is needed during development.

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `GOLDAPI_KEY` | (none) | GoldAPI.io key for live prices (optional) |
| `DATABASE_URL` | `sqlite:///./data/pmtracker.db` | SQLite database path |

Without a `GOLDAPI_KEY`, the app uses fallback prices: Gold $2,650/oz, Silver $30/oz, Platinum $950/oz, Palladium $1,000/oz.

---

## Backend Architecture

### Entry Point: `app/main.py`

- Creates all database tables on startup (`Base.metadata.create_all`)
- Seeds 4 metals and 21 bullion products on first run (only if metals table is empty)
- Configures CORS for `http://localhost:3000` and `http://127.0.0.1:3000`
- Mounts all route modules
- `/api/admin/reseed` — unprotected endpoint to force-reseed metals and products (clears existing ones)

### Database: `app/database.py` + `app/models.py`

SQLAlchemy 2.x with SQLite. Tables:

| Table | Purpose |
|---|---|
| `metals` | Metal types (Gold, Silver, Platinum, Palladium). `symbol` used for price lookups |
| `products` | Bullion products with `weight_oz` and FK to `metals` |
| `holdings` | User's purchased items with quantity, purchase price, optional metadata |
| `app_settings` | Key-value store for `password_hash` and `jwt_secret` |

**No migration framework is used.** Schema changes require either a new `migrate_db.py` script or manual SQLite commands. `Base.metadata.create_all` only creates missing tables; it does not alter existing columns.

Always call `get_db()` via FastAPI dependency injection — never create sessions directly in route handlers.

### Authentication: `app/auth.py`

Single-user app. No user table. The password hash and JWT secret are stored in `app_settings`.

- **First run:** `GET /api/auth/status` → `password_configured: false` → user calls `POST /api/auth/setup`
- **Subsequent runs:** `POST /api/auth/login` with password → returns 24-hour JWT
- **Protected routes:** Use `Depends(get_current_user)` — raises 401 if token is missing/invalid/expired
- JWT algorithm: HS256; expiry: 24 hours
- Password hashing: bcrypt via passlib

### Schemas: `app/schemas.py`

All request and response shapes are defined as Pydantic models. Key validators:
- Strings must be non-empty and within max length
- `weight_oz`, `quantity`, `purchase_price_per_oz` must be positive
- `purchase_date` cannot be in the future
- `premium_paid` must be >= 0

Always add new fields to both the `Create` schema (input) and the base/response schema (output).

### Price Service: `app/services/price_service.py`

Singleton `price_service` instance. Tries GoldAPI.io first, falls back to Metals-API, then to static fallback prices.

- Prices are cached for **30 minutes** in memory
- If an API returns a rate-limit error, it backs off for **1 hour**
- Metal symbols used for lookups: `gold`, `silver`, `platinum`, `palladium` (match `Metal.symbol` in DB)

---

## Frontend Architecture

### State Management

No Redux or external state library. State lives in:
- `AuthContext` (`src/contexts/AuthContext.jsx`) — authentication state, token, setup/login/logout
- `App.jsx` — application data (prices, portfolio summary, holdings list, modal state)

### API Client: `src/services/api.js`

Single module with a `fetchJson()` helper that:
- Prepends the base URL (`VITE_API_URL` env var or `http://localhost:8000`)
- Attaches `Authorization: Bearer <token>` from `localStorage['pmtracker_token']`
- On 401 response: clears the token and reloads the page (forces re-login)

All API calls go through this module. Never call `fetch()` directly in components.

### Component Conventions

- Components are plain functional React components with hooks
- No TypeScript; no prop-types library
- No external UI component library — all styling is plain CSS in `index.css`
- Currency values formatted with `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`
- Metal color coding is applied via CSS classes (`.metal-gold`, `.metal-silver`, etc.)

### Build

```bash
cd frontend
npm run build     # outputs to frontend/dist/
npm run preview   # serve the production build locally
```

The Vite build output is served by Nginx in the production Docker container (port 8080 internally, mapped to 3000 by Docker Compose).

---

## API Reference

### Public (no auth required)

| Method | Path | Description |
|---|---|---|
| GET | `/` | API info |
| GET | `/api/health` | Health check |
| GET | `/api/auth/status` | Returns `{ password_configured: bool }` |
| POST | `/api/auth/setup` | First-time password setup; returns JWT |
| POST | `/api/auth/login` | Login with password; returns JWT |
| POST | `/api/admin/reseed` | Force reseed metals and products |

### Protected (Bearer token required)

| Method | Path | Description |
|---|---|---|
| GET | `/api/metals` | List all metals |
| POST | `/api/metals` | Create a metal |
| GET | `/api/metals/{id}` | Get a metal |
| GET | `/api/products` | List products (filter: `?metal_id=`) |
| POST | `/api/products` | Create a product |
| GET | `/api/products/{id}` | Get a product |
| DELETE | `/api/products/{id}` | Delete a product |
| GET | `/api/holdings` | List all holdings |
| POST | `/api/holdings` | Create a holding |
| GET | `/api/holdings/{id}` | Get a holding |
| PUT | `/api/holdings/{id}` | Update a holding |
| DELETE | `/api/holdings/{id}` | Delete a holding |
| GET | `/api/portfolio/prices` | Current spot prices |
| GET | `/api/portfolio/summary` | Aggregate stats (cost, value, P/L, allocation) |
| GET | `/api/portfolio/holdings` | Holdings with calculated current values and P/L |

Interactive API docs available at `http://localhost:8000/docs` when running.

---

## Key Conventions

### Backend

- **Dependency injection:** Always use `db: Session = Depends(get_db)` and `current_user = Depends(get_current_user)` in route function signatures.
- **Error responses:** Use `HTTPException` with appropriate status codes. 404 for missing resources, 400 for bad input, 401 for auth failures, 409 for conflicts (e.g., duplicate names).
- **Schema separation:** Input schemas (e.g., `HoldingCreate`) are separate from response schemas (e.g., `Holding`). Add `model_config = ConfigDict(from_attributes=True)` to response schemas for ORM compatibility.
- **No direct SQL:** Use SQLAlchemy ORM queries; avoid raw SQL strings.
- **Pinned dependencies:** `requirements.txt` uses exact versions. Update intentionally, not incidentally.

### Frontend

- **API calls in `App.jsx`:** Data fetching and mutation handlers live in `App.jsx` and are passed as props to child components. Components do not call the API directly.
- **Token storage:** `localStorage` key is `pmtracker_token`. The `AuthContext` is the single source of truth for auth state.
- **No routing library:** The app is a single-page application without React Router. Navigation is handled by conditional rendering based on auth state.
- **Modal pattern:** `AddHoldingModal` handles both add and edit modes based on whether an `editingHolding` prop is passed.

### Git

- Keep commits focused and descriptive
- No CI/CD pipeline is configured; testing is manual per `TEST_PLAN.md`

---

## Common Tasks

### Adding a new API endpoint

1. Define Pydantic schemas in `backend/app/schemas.py`
2. Add the ORM model in `backend/app/models.py` if a new table is needed
3. Create or update the route in the appropriate `backend/app/routes/*.py` file
4. Register the router in `backend/app/main.py` if it's a new router module
5. Add the corresponding function to `frontend/src/services/api.js`
6. Call the API from `App.jsx` or a component

### Adding a new metal/product type

New metals and products can be added via the API (`POST /api/metals`, `POST /api/products`) while the app is running. To add them to the seed data, edit the `products_data` list in `backend/app/main.py` (both in `seed_database` and `reseed_database`).

### Changing the database schema

1. Edit `backend/app/models.py`
2. Write a migration script in `backend/app/migrate_db.py` using raw SQLAlchemy or SQLite `ALTER TABLE` statements
3. Run the migration against the live database
4. `create_all` will only help for entirely new tables, not column additions

### Running the manual test suite

```bash
# Bash (Linux/macOS)
./test_api.sh

# PowerShell (Windows)
./test_api.ps1
```

Both scripts test auth, CRUD operations, and input validation against a running backend instance.

---

## Security Notes

- The application is designed for **local/self-hosted use only**. CORS is locked to `localhost`.
- There is **one application password** — no user accounts or roles.
- JWT secrets are auto-generated and stored in the database; they are not configurable via environment variables.
- Docker containers run as **non-root users** (`appuser` in backend, unprivileged nginx in frontend).
- Nginx sets `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, and `Referrer-Policy` headers.
- `/api/admin/reseed` is **unauthenticated** — it will delete all metals and products. Do not expose this service publicly.
