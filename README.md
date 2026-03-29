# FinVest — FinTech Investment Platform

A microservices-based personal finance and investment platform built for the IT4020 Microservices Assignment at SLIIT.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (:5173)                    │
│            Tailwind CSS + Axios + Recharts                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ All requests via /api/*
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway (:8000)                        │
│              FastAPI + httpx (async proxy)                   │
│         /health • logging • CORS • timeout handling         │
└───┬──────────┬──────────────┬──────────────┬────────────────┘
    │          │              │              │
    ▼          ▼              ▼              ▼
┌────────┐ ┌────────┐ ┌────────────┐ ┌────────────┐
│ User   │ │ Asset  │ │Transaction │ │ Analytics  │
│ Service│ │ Service│ │  Service   │ │  Service   │
│ :8001  │ │ :8002  │ │   :8003    │ │   :8004    │
│        │ │        │ │            │ │            │
│ SQLite │ │ SQLite │ │   SQLite   │ │   SQLite   │
│user.db │ │asset.db│ │ txn.db     │ │analytics.db│
└────────┘ └───┬────┘ └────────────┘ └────┬───────┘
               │                          │
               ▼                          ▼
         CoinGecko API             Frankfurter API
        (live crypto $)            (USD → LKR rate)
```

## Prerequisites

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **pip** (comes with Python)

## Installation

### 1. Clone / extract the project

```bash
cd fintech-micro-investing
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Option A: Start all at once

**Linux / macOS:**
```bash
chmod +x start_all.sh
./start_all.sh
```

**Windows:**
```cmd
start_all.bat
```

### Option B: Start services individually

Open separate terminals for each:

```bash
# Terminal 1 — User Service
cd services/user_service
uvicorn main:app --port 8001

# Terminal 2 — Asset Service
cd services/asset_service
uvicorn main:app --port 8002

# Terminal 3 — Transaction Service
cd services/transaction_service
uvicorn main:app --port 8003

# Terminal 4 — Analytics Service
cd services/analytics_service
uvicorn main:app --port 8004

# Terminal 5 — API Gateway
cd gateway
uvicorn main:app --port 8000

# Terminal 6 — Frontend
cd frontend
npm run dev
```

## Accessing the Application

| Component            | URL                              |
|----------------------|----------------------------------|
| **Frontend**         | http://localhost:5173             |
| **API Gateway**      | http://localhost:8000             |
| **Gateway Swagger**  | http://localhost:8000/docs        |
| **User Service**     | http://localhost:8001/docs        |
| **Asset Service**    | http://localhost:8002/docs        |
| **Transaction Svc**  | http://localhost:8003/docs        |
| **Analytics Service**| http://localhost:8004/docs        |
| **Health Check**     | http://localhost:8000/health      |

## Free External APIs

| API             | Purpose               | URL                                        | Auth Required |
|-----------------|-----------------------|--------------------------------------------|---------------|
| **CoinGecko**   | Live crypto prices    | https://api.coingecko.com/api/v3           | No            |
| **Frankfurter** | USD → LKR exchange    | https://api.frankfurter.app                | No            |

## Team Member Contributions

| Member | Service Owned            | Tech Responsibility                                             |
|--------|--------------------------|----------------------------------------------------------------|
| 1      | User & KYC Service       | User registration, profiles, KYC verification, SQLite DB       |
| 2      | Asset & Market Service   | Asset management, CoinGecko integration, price caching         |
| 3      | Transaction Service      | Buy/sell orders, status lifecycle, portfolio summary            |
| 4      | Analytics Service        | Savings goals, Frankfurter API, LKR conversion, portfolio view |

## Tech Stack

### Backend
- **Python 3.11+** with **FastAPI**
- **SQLAlchemy** (ORM) with **SQLite** (one DB per service)
- **Pydantic v2** for validation
- **httpx** for async HTTP in the gateway
- **requests** for external API calls

### Frontend
- **React 18** + **Vite**
- **Tailwind CSS** (CDN)
- **Axios** for API calls
- **React Router v6** for navigation
- **Recharts** for charts

## Troubleshooting

### Port conflicts
If a port is already in use, you can specify a different port:
```bash
uvicorn main:app --port 8010  # use any available port
```
Remember to update the gateway's `routes.py` if you change service ports.

### CORS issues
All services have CORS enabled with `allow_origins=["*"]`. If you still encounter CORS errors, ensure the gateway is running and you're accessing services through it (port 8000).

### CoinGecko rate limits
The free CoinGecko API has rate limits (~10-30 req/min). The asset service caches prices for 60 seconds to minimize calls. If you see "stale_data: true", the cache is being used as a fallback.

### Frankfurter API unavailable
If the Frankfurter API is down, the analytics service automatically falls back to a hardcoded rate of 320.0 LKR/USD with `fallback_rate: true`.

### SQLite database files
Database files (`user.db`, `asset.db`, `transaction.db`, `analytics.db`) are auto-created on first run in each service directory. To reset, simply delete the `.db` files and restart.

## License

This project is created for educational purposes as part of the IT4020 module at SLIIT.
