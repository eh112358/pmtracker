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

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
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

### Spot Price API

By default, the application uses fallback prices for development. To enable live spot prices:

1. Sign up for an API key at [metals-api.com](https://metals-api.com) or similar service
2. Set the environment variable:
   ```bash
   METALS_API_KEY=your_api_key_here
   ```

Or add it to `docker-compose.yml`:
```yaml
environment:
  - METALS_API_KEY=your_api_key_here
```

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
