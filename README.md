# PM Tracker - Precious Metals Portfolio Tracker

A local web application to track the purchase prices and current value of your physical precious metals investments.

## Features

- Track holdings of Gold, Silver, Platinum, and Palladium
- Pre-loaded product catalog (American Eagles, Maple Leafs, bars, etc.)
- Real-time spot price display
- Portfolio summary with total cost, current value, and profit/loss
- Allocation breakdown by metal type
- Record purchase details: date, price, premium, dealer, storage location

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Running the Application

1. Clone or navigate to the project directory:
   ```bash
   cd pmtracker
   ```

2. **Set up your API key** (for live spot prices):
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Get a free API key from https://www.goldapi.io/ (300 requests/month)
   # Edit .env and add your API key:
   # GOLDAPI_KEY=your-actual-key-here
   ```

   **Note**: The application will work without an API key using fallback prices for testing.

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Stopping the Application

```bash
docker-compose down
```

## Development Setup

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

## Configuration

### Environment Setup

The application uses a `.env` file for configuration. This file is **not tracked in Git** for security.

**First-time setup**:
```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor
```

**Required configuration**:
```bash
# .env file
GOLDAPI_KEY=your-actual-key-here
```

### Spot Price API

The application supports two API providers:

**Option 1: GoldAPI.io** (Recommended)
- Free tier: 300 requests/month
- Sign up: https://www.goldapi.io/
- Set `GOLDAPI_KEY` in `.env` file

**Option 2: Metals-API.com** (Alternative)
- Set `METALS_API_KEY` in `.env` file

**Fallback**: If no API key is configured, the application uses static fallback prices for testing.

For production deployment and advanced configuration options, see [docs/SECRET_MANAGEMENT.md](docs/SECRET_MANAGEMENT.md).

## Project Structure

```
pmtracker/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       ├── database.py
│       ├── routes/
│       │   ├── holdings.py
│       │   ├── products.py
│       │   ├── metals.py
│       │   └── portfolio.py
│       └── services/
│           └── price_service.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── nginx.conf
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── Dashboard.jsx
│       │   ├── HoldingsTable.jsx
│       │   ├── AddHoldingModal.jsx
│       │   └── AllocationChart.jsx
│       └── services/
│           └── api.js
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/holdings` | List all holdings |
| POST | `/api/holdings` | Add new holding |
| PUT | `/api/holdings/{id}` | Update holding |
| DELETE | `/api/holdings/{id}` | Delete holding |
| GET | `/api/products` | List product catalog |
| GET | `/api/metals` | List metals |
| GET | `/api/portfolio/prices` | Get current spot prices |
| GET | `/api/portfolio/summary` | Get portfolio summary |
| GET | `/api/portfolio/holdings` | Get holdings with calculated values |

## Data Persistence

The SQLite database is stored in `backend/data/pmtracker.db` and is mounted as a Docker volume, so your data persists between container restarts.

## License

MIT
