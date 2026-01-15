# PM Tracker - Precious Metals Portfolio Tracker

A local web application to track the purchase prices and current value of your physical precious metals investments.

## Features

- **Password Protection** - Secure your portfolio data with password authentication
- **Track Holdings** - Gold, Silver, Platinum, and Palladium products
- **Pre-loaded Product Catalog** - American Eagles, Maple Leafs, Krugerrands, bars, and more
- **Live Spot Prices** - Real-time gold and silver prices via GoldAPI.io
- **Portfolio Summary** - Total cost basis, current value, and profit/loss calculations
- **Allocation Breakdown** - Visual breakdown by metal type
- **Detailed Records** - Purchase date, price per oz, premium, dealer, storage location, and notes

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- (Optional) GoldAPI.io API key for live spot prices

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pmtracker.git
   cd pmtracker
   ```

2. Configure live spot prices (optional):
   ```bash
   cp .env.example .env
   # Edit .env and add your GoldAPI key
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build -d
   ```

4. Access the application:
   - **Application**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs

5. On first visit, create a password (minimum 8 characters) to secure your data.

### Stopping the Application

```bash
docker-compose down
```

## Spot Price Configuration (GoldAPI.io)

The application uses [GoldAPI.io](https://www.goldapi.io/) for live gold and silver spot prices.

### Getting an API Key

1. Sign up for a free account at https://www.goldapi.io/
2. Free tier includes **300 requests/month**
3. Copy your API key

### Configuring the API Key

Create a `.env` file in the project root:

```bash
GOLDAPI_KEY=your_api_key_here
```

Or add it directly to `docker-compose.yml`:

```yaml
environment:
  - GOLDAPI_KEY=your_api_key_here
```

### Rate Limiting

- Prices are cached for **30 minutes** to conserve API calls
- Each refresh makes **2 API calls** (gold and silver)
- If rate limited, the app automatically uses fallback prices
- Free tier: ~150 refreshes per month

### Without an API Key

The application works without an API key using fallback prices:
- Gold: $2,650.00/oz
- Silver: $30.00/oz

## Development Setup

### Backend (FastAPI + Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm start
```

For development, set the API URL in the frontend:
```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
pmtracker/
├── docker-compose.yml
├── .env                    # API keys (create from .env.example)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── data/               # SQLite database (persisted)
│   └── app/
│       ├── main.py
│       ├── auth.py         # JWT authentication
│       ├── models.py
│       ├── schemas.py      # Pydantic models with validation
│       ├── database.py
│       ├── routes/
│       │   ├── auth.py     # Login/setup endpoints
│       │   ├── holdings.py
│       │   ├── products.py
│       │   ├── metals.py
│       │   └── portfolio.py
│       └── services/
│           └── price_service.py  # GoldAPI integration
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── components/
│       │   ├── Login.jsx
│       │   ├── Dashboard.jsx
│       │   ├── HoldingsTable.jsx
│       │   ├── AddHoldingModal.jsx
│       │   └── AllocationChart.jsx
│       ├── contexts/
│       │   └── AuthContext.jsx
│       └── services/
│           └── api.js
├── TEST_PLAN.md
├── test_api.ps1            # PowerShell test script
├── test_api.sh             # Bash test script
└── README.md
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/status` | Check if password is configured |
| POST | `/api/auth/setup` | First-time password setup |
| POST | `/api/auth/login` | Login with password |

### Portfolio (requires authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolio/prices` | Get current spot prices |
| GET | `/api/portfolio/summary` | Get portfolio summary |
| GET | `/api/portfolio/holdings` | Get holdings with calculated values |

### Holdings (requires authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/holdings` | List all holdings |
| GET | `/api/holdings/{id}` | Get specific holding |
| POST | `/api/holdings` | Add new holding |
| PUT | `/api/holdings/{id}` | Update holding |
| DELETE | `/api/holdings/{id}` | Delete holding |

### Products & Metals (requires authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List product catalog |
| GET | `/api/products?metal_id=1` | Filter products by metal |
| GET | `/api/metals` | List available metals |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/reseed` | Repopulate metals and products |

## Data Persistence

- **Database**: SQLite stored in `backend/data/pmtracker.db`
- **Docker Volume**: Data persists between container restarts
- **Backup**: Simply copy the `backend/data/` directory

## Security

- Password protected with bcrypt hashing
- JWT tokens with 24-hour expiry
- Input validation on all endpoints
- Tokens stored in browser localStorage

## Troubleshooting

### "Failed to fetch" errors
1. Ensure both containers are running: `docker ps`
2. Check backend logs: `docker logs pmtracker-backend`
3. Verify backend is accessible: http://localhost:8000/api/health

### Database issues
Reset the database:
```bash
rm backend/data/pmtracker.db
docker-compose restart backend
```

### Reseed products
```bash
curl -X POST http://localhost:8000/api/admin/reseed
```

## License

MIT
