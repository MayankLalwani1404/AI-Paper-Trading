# AI Paper Trading - Complete Setup & Run Guide

Production-grade AI-powered paper trading platform with Next.js frontend and FastAPI backend.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (for PostgreSQL)
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- npm or yarn (package manager)

### Option 1: Run Everything Together

```bash
cd '/home/mayank/Desktop/AI Paper Trading'
bash run_all.sh
```

This starts both backend and frontend. Access at:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Run Separately (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
bash run_backend.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
bash run_frontend.sh
```

**Terminal 3 - Testing:**
```bash
bash test_full_stack.sh
```

## 📋 Backend Setup (FastAPI)

### Initial Setup (One-time)

```bash
# Navigate to project root
cd '/home/mayank/Desktop/AI Paper Trading'

# Run setup script (if not already done)
bash setup_garuda.sh
```

This handles:
- ✅ Python venv creation
- ✅ Dependency installation
- ✅ PostgreSQL verification (Docker)
- ✅ Redis setup
- ✅ Database initialization

### Running Backend

```bash
cd backend
bash run_backend.sh
```

The backend will:
1. Activate Python venv at `backend/.venv`
2. Start Uvicorn server on `http://0.0.0.0:8000`
3. Enable auto-reload on code changes
4. Serve interactive API docs at `http://localhost:8000/docs`

### Backend Structure

```
backend/
├── api/              # REST endpoints
│   ├── health.py     # Health check
│   ├── market_data.py # Market data endpoints
│   ├── indicators.py  # Indicators endpoints
│   ├── trading.py     # Trading endpoints
│   └── router.py      # Main router
├── market_data/      # Market data service
│   ├── symbols.py    # Symbol registry
│   ├── cache.py      # Redis caching
│   └── service.py    # Data fetching
├── indicators/       # Technical indicators
│   ├── technical.py  # Indicator algorithms
│   ├── schemes.py    # Data schemas
│   ├── service.py    # Indicator service
│   └── utils.py      # Utilities
├── trading/          # Trading logic
│   ├── models.py     # Database models
│   ├── schemes.py    # Request/response schemas
│   └── service.py    # Trading service
├── core/             # Core configuration
│   ├── config.py     # Settings
│   ├── database.py   # PostgreSQL connection
│   └── redis.py      # Redis connection
├── main.py           # FastAPI app
├── create_tables.py  # Database initialization
├── requirements.txt  # Python dependencies
└── .venv/            # Virtual environment
```

### Backend Endpoints

**Market Data:**
- `GET /market-data/symbols` - Get symbols by market
- `GET /market-data/latest-price?symbol=AAPL` - Latest price
- `GET /market-data/ohlcv?symbol=AAPL&interval=1d` - OHLCV data
- `GET /market-data/search?q=AAP` - Search symbols

**Indicators:**
- `GET /indicators/available` - Available indicators
- `POST /indicators/calculate` - Calculate indicator
- `GET /indicators/all?symbol=AAPL` - All indicators
- `GET /indicators/signals?symbol=AAPL` - Trade signals

**Trading:**
- `GET /trading/portfolio` - Portfolio overview
- `POST /trading/order` - Place order
- `GET /trading/positions` - Open positions

**Health:**
- `GET /` - Root endpoint
- `GET /health` - Health check

## 🎨 Frontend Setup (Next.js)

### Initial Setup (One-time)

```bash
cd frontend
npm install
```

Installs all dependencies:
- React 18.3 & Next.js 14
- TypeScript
- Tailwind CSS
- SWR for data fetching
- Recharts for charts
- Lucide React for icons

### Running Frontend

```bash
cd frontend
bash run_frontend.sh
```

The frontend will:
1. Check for dependencies (install if needed)
2. Start Next.js dev server on `http://localhost:3000`
3. Enable hot reload on code changes
4. Connect to backend at `http://localhost:8000`

### Frontend Pages

- **Dashboard** (`/`) - Portfolio overview, positions, quick actions
- **Portfolio** (`/portfolio`) - Detailed holdings table with P&L
- **Market Scanner** (`/market`) - Technical indicators & signals
- **Charts** (`/charts`) - Interactive OHLCV charts with intervals
- **Trading** (`/trading`) - Order placement interface

### Frontend Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx         # Dashboard
│   │   ├── portfolio/page.tsx
│   │   ├── market/page.tsx
│   │   ├── charts/page.tsx
│   │   ├── trading/page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── Sidebar.tsx      # Navigation
│   │   ├── SignalCard.tsx   # Trade signals
│   │   └── PriceChart.tsx   # Charts
│   └── lib/
│       ├── api.ts          # API client
│       └── hooks.ts        # Data hooks
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── run_frontend.sh
```

## 🧪 Testing

### Full Stack Test

Verify all endpoints are working:

```bash
bash test_full_stack.sh
```

Tests:
- ✅ Backend health check
- ✅ Market data API
- ✅ Indicators API
- ✅ Trading API
- ✅ Frontend connectivity

### Manual Testing

**Backend API:**
```bash
# Get symbols
curl http://localhost:8000/market-data/symbols?market=US

# Get latest price
curl http://localhost:8000/market-data/latest-price?symbol=AAPL

# Get signals
curl http://localhost:8000/indicators/signals?symbol=AAPL

# View API docs
open http://localhost:8000/docs
```

**Frontend:**
1. Open `http://localhost:3000`
2. Navigate through pages
3. Check browser console for errors
4. Verify real-time data updates (5-60s intervals)

## 📊 Feature Overview

### Market Data
- Real-time prices via Yahoo Finance
- Fallback to local CSV datasets
- 5-60 second refresh rates
- Multi-market support (US, NSE, BSE, Crypto, Index)

### Technical Indicators
- SMA, EMA (trend analysis)
- RSI (momentum)
- MACD (trend following)
- Bollinger Bands (volatility)
- ATR (volatility measurement)
- Stochastic (momentum)
- Support/Resistance levels

### Trading Signals
- AI-powered score (-100 to +100)
- Recommendations: STRONG BUY → STRONG SELL
- Multi-indicator analysis
- Signal confidence level

### Portfolio Management
- Position tracking
- Gain/loss calculation
- Performance analytics
- Order history

## 🔧 Configuration

### Backend Config

Edit `backend/core/config.py`:
```python
DATABASE_URL = "postgresql://papertrader:papertraderpass@localhost/papertrading"
REDIS_URL = "redis://localhost:6379"
SECRET_KEY = "your-secret-key"
```

### Frontend Config

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database

PostgreSQL runs in Docker:
```bash
# Container name: papertrading-postgres
# Port: 5432
# User: papertrader
# Password: papertraderpass
# Database: papertrading
```

Verify:
```bash
docker exec -it papertrading-postgres psql -U papertrader -d papertrading -c "SELECT 1;"
```

### Redis

Redis runs in Docker:
```bash
# Port: 6379
# No authentication required
```

Verify:
```bash
redis-cli ping
# Output: PONG
```

## 📈 Data Flow

1. **Frontend** requests data from **Backend** API
2. **Backend** checks **Redis** cache (instant)
3. If cache miss, fetches from **Yahoo Finance** API
4. Falls back to **Local CSV** datasets
5. Response cached in **Redis** with TTL
6. **Frontend** updates UI in real-time
7. **Database** persists trading history

## 🚨 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

**PostgreSQL connection error:**
```bash
# Verify Docker container
docker ps | grep postgres

# Check logs
docker logs papertrading-postgres

# Restart container
docker restart papertrading-postgres
```

**Module not found errors:**
```bash
# Reinstall dependencies
cd backend
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend Issues

**Cannot connect to backend:**
- Check backend is running: `ps aux | grep uvicorn`
- Verify backend URL: `curl http://localhost:8000/health`
- Update `NEXT_PUBLIC_API_URL` in `.env.local`

**Symbols not loading:**
```bash
curl http://localhost:8000/market-data/symbols
```

**Port 3000 already in use:**
```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in frontend/run_frontend.sh
```

### Database Issues

**PostgreSQL fails to start:**
```bash
docker logs papertrading-postgres
docker restart papertrading-postgres
```

**Redis connection failed:**
```bash
# Check if running
redis-cli ping

# Restart if needed
docker restart redis-service
```

## 📚 API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Next Steps

1. Start the services with `bash run_all.sh`
2. Open http://localhost:3000 in browser
3. Explore Dashboard and Market Scanner
4. Try placing test trades
5. Monitor real-time signals and indicators
6. Review API documentation at http://localhost:8000/docs

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Review logs in respective terminals
3. Verify all prerequisites are installed
4. Check backend/frontend configuration
5. Ensure Docker services are running

## 📦 Deployment

For production deployment, see:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`

---

**Happy Trading! 🚀**
