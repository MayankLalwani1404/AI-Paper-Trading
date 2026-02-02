# 🚀 AI Paper Trading Platform - Complete & Ready to Run

## ⚡ Super Quick Start (2 Minutes)

### Option 1: Run Everything at Once
```bash
cd '/home/mayank/Desktop/AI Paper Trading'
bash run_all.sh
```

Then open in browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

### Option 2: Run Separately (Better for Development)

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
bash test_all.sh
```

---

## 📋 What's Included

### ✅ Backend (FastAPI + Python)
- Market data API with Yahoo Finance integration
- 8 technical indicators with signal generation
- PostgreSQL database (running in Docker)
- Redis cache for performance
- 20+ REST endpoints
- Interactive API documentation

### ✅ Frontend (Next.js + React)
- Dashboard with portfolio overview
- Portfolio management page
- Real-time market scanner
- Interactive trading charts
- Order placement interface
- Responsive Tailwind CSS design

### ✅ Infrastructure
- Docker PostgreSQL container
- Redis cache
- Python virtual environment
- npm dependencies
- Automated setup scripts

---

## 📚 Full Documentation

| Document | Purpose |
|----------|---------|
| **QUICKSTART.md** | Step-by-step setup guide |
| **DEPLOYMENT_GUIDE.md** | Complete feature overview & deployment |
| **API_DOCUMENTATION.md** | Detailed API reference |
| **backend/README.md** | Backend-specific documentation |
| **frontend/README.md** | Frontend-specific documentation |

---

## 🎯 Features

### Market Data
- Real-time prices via Yahoo Finance
- Local CSV fallback
- Multi-market support (US, NSE, BSE, Crypto)
- 5-24 hour caching

### Technical Indicators (8 Types)
- **Trend**: SMA, EMA
- **Momentum**: RSI, Stochastic  
- **Trend-Following**: MACD
- **Volatility**: Bollinger Bands, ATR
- **Support/Resistance**: Calculated levels

### Trading Signals
- AI-powered confidence scoring (-100 to +100)
- Multi-indicator analysis
- Buy/Sell recommendations

### Portfolio Management
- Real-time position tracking
- Gain/loss calculation
- Performance analytics

---

## 🚀 Running the Platform

### 1. Backend is Ready ✅
```bash
cd backend
bash run_backend.sh
```
- Starts on http://localhost:8000
- API docs at http://localhost:8000/docs

### 2. Frontend is Ready ✅
```bash
cd frontend
bash run_frontend.sh
```
- Starts on http://localhost:3000
- Auto-installs dependencies if needed

### 3. Both Together ✅
```bash
bash run_all.sh
```
- Starts backend and frontend
- Press Ctrl+C to stop both

---

## 🧪 Testing

### Complete Test Suite
```bash
bash test_all.sh
```

Tests infrastructure, APIs, performance, and connectivity.

### Backend Only
```bash
bash test_backend.sh
```

### Quick Stack Test
```bash
bash test_full_stack.sh
```

---

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Web UI |
| **Backend** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Interactive docs |
| **PostgreSQL** | localhost:5432 | Database (Docker) |
| **Redis** | localhost:6379 | Cache |

---

## 📂 Project Structure

```
AI Paper Trading/
├── backend/                 # FastAPI backend
│   ├── api/                # REST endpoints
│   ├── market_data/        # Data fetching
│   ├── indicators/         # Technical indicators
│   ├── trading/            # Trading logic
│   ├── core/               # Config & database
│   ├── .venv/              # Python venv
│   └── run_backend.sh
│
├── frontend/               # Next.js frontend
│   ├── src/app/            # Pages
│   ├── src/components/     # React components
│   ├── src/lib/            # API client & hooks
│   └── run_frontend.sh
│
├── datasets/               # Historical data (CSV)
├── run_all.sh              # Start both services
├── test_all.sh             # Test suite
└── QUICKSTART.md           # Setup guide
```

---

## 🔧 First-Time Setup

If not already done, initialize everything:

```bash
bash setup_garuda.sh
```

This handles:
- ✅ Python venv creation
- ✅ Dependency installation
- ✅ Database initialization
- ✅ Redis setup
- ✅ Service verification

---

## 💻 System Requirements

- **OS**: Linux (Garuda/Arch tested)
- **Python**: 3.11+ (backend)
- **Node.js**: 18+ (frontend)
- **Docker**: For PostgreSQL
- **RAM**: 2GB minimum
- **Disk**: 1GB free space

---

## 🎯 Usage Guide

### 1. View Dashboard
- Open http://localhost:3000
- See portfolio overview
- Monitor positions

### 2. Check Market Data
- Go to "Market Scanner" page
- Select any symbol
- View live indicators
- See AI signals

### 3. Analyze Charts
- Go to "Charts" page
- Choose symbol and timeframe
- View OHLCV data

### 4. Place a Trade
- Go to "Trading" page
- Select BUY or SELL
- Enter quantity and price
- Confirm order

### 5. Monitor Portfolio
- Go to "Portfolio" page
- See all holdings
- Track P&L

---

## 📊 API Examples

### Get Latest Price
```bash
curl http://localhost:8000/market-data/latest-price?symbol=AAPL
```

### Get Trade Signals
```bash
curl http://localhost:8000/indicators/signals?symbol=AAPL
```

### Get Portfolio
```bash
curl http://localhost:8000/trading/portfolio
```

### Interactive Docs
```
http://localhost:8000/docs
```

---

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Check if port is in use
lsof -i :8000

# Check PostgreSQL
docker ps | grep postgres

# Restart services
docker restart papertrading-postgres
cd backend && bash run_backend.sh
```

### Frontend won't start?
```bash
# Install dependencies
cd frontend
npm install

# Start again
bash run_frontend.sh
```

### No data showing?
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check API endpoints
curl http://localhost:8000/market-data/latest-price?symbol=AAPL

# Check browser console for errors
```

### Port already in use?
```bash
# Find process
lsof -i :3000    # Frontend
lsof -i :8000    # Backend
lsof -i :5432    # Database

# Kill process
kill -9 <PID>
```

---

## 📈 Performance

| Endpoint | Time | Cached |
|----------|------|--------|
| Market data | <500ms | <100ms |
| Indicators | <1s | <200ms |
| Trading API | <200ms | <50ms |
| Frontend load | <2s | - |

---

## 🎨 Frontend Pages

### Dashboard (`/`)
- Portfolio value & cash balance
- Open positions list
- Quick action buttons

### Portfolio (`/portfolio`)
- All holdings table
- Entry price vs current price
- Gain/loss tracking
- Return percentage

### Market Scanner (`/market`)
- Symbol search
- Real-time indicators
- Trading signals
- AI recommendation

### Charts (`/charts`)
- Interactive OHLCV chart
- Multiple intervals (1m-1w)
- Symbol selector
- Live data updates

### Trading (`/trading`)
- Order form (BUY/SELL)
- Quantity & price input
- Order summary
- Confirmation

---

## 🔗 API Endpoints

### Market Data (8 endpoints)
- `GET /market-data/symbols`
- `GET /market-data/latest-price`
- `GET /market-data/ohlcv`
- `GET /market-data/search`
- Plus 4 more...

### Indicators (7 endpoints)
- `GET /indicators/available`
- `POST /indicators/calculate`
- `GET /indicators/signals`
- Plus 4 more...

### Trading (3 endpoints)
- `GET /trading/portfolio`
- `POST /trading/order`
- `GET /trading/positions`

### Health (2 endpoints)
- `GET /`
- `GET /health`

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js**: https://nextjs.org
- **React**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **yfinance**: https://pypi.org/project/yfinance/

---

## 🚀 Quick Commands

```bash
# Start everything
bash run_all.sh

# Start backend only
cd backend && bash run_backend.sh

# Start frontend only
cd frontend && bash run_frontend.sh

# Test everything
bash test_all.sh

# Make all scripts executable
bash make_executable.sh

# Setup (first time only)
bash setup_garuda.sh
```

---

## 📞 Support

### Issues?
1. Check logs in terminal
2. Verify services running: `docker ps`, `ps aux | grep python`
3. Test endpoints: `curl http://localhost:8000/health`
4. Review documentation in respective folders

### Stuck?
1. Read **QUICKSTART.md** for detailed setup
2. Check **DEPLOYMENT_GUIDE.md** for troubleshooting
3. View API docs: http://localhost:8000/docs
4. Check browser console for frontend errors

---

## ✨ What You Can Do Now

✅ **Real-time trading data** - Live prices, historical charts  
✅ **Technical analysis** - 8 indicators, support/resistance  
✅ **AI signals** - Confidence-scored recommendations  
✅ **Portfolio tracking** - Monitor positions and P&L  
✅ **Order management** - Place trades, track history  
✅ **Interactive UI** - Modern, responsive design  
✅ **REST API** - Programmatic access to all features  
✅ **Real-time updates** - 5-60 second refresh rates  

---

## 🎉 You're All Set!

Your AI Paper Trading Platform is **complete and ready to use**!

### Next Steps:
1. Run: `bash run_all.sh`
2. Open: http://localhost:3000
3. Start trading! 📈

---

## 📝 File Summary

| File | Purpose |
|------|---------|
| `run_all.sh` | Start backend + frontend |
| `test_all.sh` | Complete test suite |
| `setup_garuda.sh` | Initial setup |
| `QUICKSTART.md` | Setup guide |
| `DEPLOYMENT_GUIDE.md` | Features & deployment |
| `API_DOCUMENTATION.md` | API reference |

---

**Your AI Paper Trading Platform is ready to go!** 🚀

```bash
cd '/home/mayank/Desktop/AI Paper Trading'
bash run_all.sh
```

Open http://localhost:3000 and start trading!

Happy Trading! 📈💰🤖
