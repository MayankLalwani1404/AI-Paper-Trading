# AI Paper Trading Platform

An AI-assisted **paper trading platform** designed to simulate stock market trading while providing intelligent decision support using machine learning and natural language processing.

This project is built as a **research, learning, and prototyping platform** for algorithmic trading, AI-driven stock analysis, and portfolio management — without using real money.

---

## 🚀 Project Overview

The platform allows users to:

- Trade stocks using **virtual capital** (paper trading)
- Maintain portfolios, positions, and trade history
- Analyze market data using **advanced technical indicators**
- Use AI to assist with:
  - Stock screening and filtering
  - Pattern recognition and chart analysis
  - Signal generation and trade scoring
  - Intelligent trade decision support

**Current Status:** Backend infrastructure complete with market data, indicators, and trading APIs. Frontend development ready to begin.

---

## 🏗️ Current Architecture

```
AI Paper Trading/
├── backend/                    # ✅ COMPLETE
│   ├── main.py                # FastAPI app
│   ├── api/                   # REST endpoints
│   │   ├── trading.py        # Buy/sell/portfolio
│   │   ├── health.py         # Health check
│   │   ├── market_data.py    # OHLCV, prices, symbols
│   │   └── indicators.py     # Technical analysis
│   ├── core/                  # Infrastructure
│   │   ├── config.py         # Settings & env vars
│   │   ├── database.py       # SQLAlchemy + PostgreSQL
│   │   └── redis.py          # Redis caching
│   ├── trading/               # Business logic
│   │   ├── models.py         # Account, Position, Trade
│   │   ├── service.py        # Buy/sell execution
│   │   └── schemes.py        # Request/response schemas
│   ├── market_data/           # NEW: Market data layer
│   │   ├── symbols.py        # Symbol registry & metadata
│   │   ├── cache.py          # Redis caching with TTL
│   │   └── service.py        # Yahoo Finance + local CSV
│   ├── indicators/            # Technical analysis
│   │   ├── technical.py      # SMA, EMA, RSI, MACD, Bollinger, ATR, Stochastic
│   │   ├── schemes.py        # Indicator schemas
│   │   └── service.py        # Indicator calculations & signals
│   └── datasets/              # ✅ Local datasets (offline)
├── frontend/                  # ⬜ TO BUILD: Next.js + TypeScript
├── .gitignore                # ✅ Configured (datasets skipped)
├── .env                       # Environment variables
├── requirements.txt          # Python dependencies
├── DEVELOPMENT_PLAN.md       # Implementation roadmap
├── API_DOCUMENTATION.md      # Complete API reference
├── SETUP_GUIDE.md           # Installation instructions
├── FRONTEND_GUIDE.md        # Frontend development guide
└── README.md                # This file
```

---

## 🛠️ Tech Stack

### Backend ✅
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Relational database (production)
- **Redis**: In-memory caching with TTL policies
- **Pandas/NumPy**: Data analysis and calculations
- **yfinance**: Market data from Yahoo Finance
- **Ollama**: Local LLM inference (ready to integrate)

### Frontend ⬜ (Coming)
- **Next.js 14**: React framework with SSR
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling
- **SWR/React Query**: Data fetching and caching
- **Chart.js / TradingView**: Financial charting
- **Zod**: Runtime schema validation

### Infrastructure
- **Docker**: Containerization (optional)
- **GitHub Actions**: CI/CD (planned)
- **AWS/Cloud**: Deployment (planned)

---

## 📊 Core Features

### ✅ Market Data
- **Yahoo Finance Integration**: Real-time and historical data
- **Local CSV Fallback**: Offline dataset support
- **Multi-Market Support**: US, NSE, BSE, Crypto, Indices
- **Symbol Registry**: Metadata and normalization
- **Redis Caching**: Intelligent TTL policies per interval

### ✅ Technical Indicators
- **Basic**: SMA, EMA, RSI
- **Advanced**: MACD, Bollinger Bands, ATR, Stochastic
- **Signal Generation**: Buy/sell recommendations
- **Pattern Detection**: Support/resistance levels
- **All calculated locally** with no cloud dependencies

### ✅ Paper Trading
- **Virtual Account**: $1,000,000 starting capital
- **Buy/Sell Simulation**: Execute trades without real money
- **Portfolio Tracking**: Positions, P&L, balance
- **Trade History**: Complete audit trail
- **Multi-symbol Support**: Diversified holdings

### ⬜ AI Features (Next Phase)
- **Ollama Integration**: Natural language queries
- **Chart Patterns**: Candlestick recognition
- **Signal Scoring**: ML-based trade ranking
- **Strategy Automation**: Simulated execution

### ⬜ Backtesting (Future Phase)
- **Historical Simulation**: Replay strategies
- **Performance Metrics**: Sharpe ratio, max drawdown
- **Optimization**: Parameter tuning

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- 8GB RAM (recommended 16GB)

### Installation (3 minutes)

```bash
# Clone repo
git clone <url> && cd "AI Paper Trading"

# Run quick setup
bash quickstart.sh

# Or manual setup:
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r requirements.txt
python backend/create_tables.py

# Start backend
uvicorn backend.main:app --reload

# Visit API docs
open http://localhost:8000/docs
```

For detailed setup, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## 📚 Documentation

### Quick References
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference with examples
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Installation and configuration
- **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)** - Roadmap and architecture
- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - Frontend development guide

### API Endpoints Summary

```
# Market Data
GET  /market-data/ohlcv?symbol=AAPL&interval=1d
GET  /market-data/latest-price?symbol=AAPL
POST /market-data/prices
GET  /market-data/search?query=apple
GET  /market-data/symbols?market=US

# Indicators
GET  /indicators/available
POST /indicators/calculate?symbol=AAPL&indicator=RSI
GET  /indicators/all/{symbol}
GET  /indicators/signals/{symbol}
POST /indicators/sma?symbol=AAPL&period=20

# Trading
POST /trading/buy    { symbol, quantity, price }
POST /trading/sell   { symbol, quantity, price }
GET  /trading/portfolio

# Health
GET  /health
```

---

## 🎯 Development Roadmap

### Phase 1: Market Data & Indicators ✅
- [x] Yahoo Finance integration with local fallback
- [x] Symbol registry with multi-market support
- [x] Redis caching with TTL policies
- [x] Technical indicator suite (SMA, EMA, RSI, MACD, Bollinger, ATR, Stochastic)
- [x] Signal generation and scoring
- [x] API endpoints for market data and indicators

### Phase 2: Frontend UI ⬜ (Next)
- [ ] Next.js project scaffolding
- [ ] Core pages: Dashboard, Portfolio, Trading, Scanner, Charts
- [ ] API client with hooks
- [ ] Portfolio visualization
- [ ] Real-time price updates
- [ ] Trade execution UI

### Phase 3: AI Integration ⬜
- [ ] Ollama setup and configuration
- [ ] Natural language query translator
- [ ] Chart pattern recognition model
- [ ] Trade signal ML classifier
- [ ] AI insights display on frontend

### Phase 4: Backtesting ⬜
- [ ] Backtesting engine
- [ ] Strategy framework
- [ ] Performance analytics
- [ ] Parameter optimization

### Phase 5: Production Ready ⬜
- [ ] Multi-user authentication (JWT)
- [ ] WebSocket real-time updates
- [ ] Advanced monitoring and logging
- [ ] Performance optimization
- [ ] Docker containerization
- [ ] Cloud deployment
- [ ] CI/CD pipelines

---

## 💡 Key Architectural Decisions

### Data Flow
```
Yahoo Finance / Local CSVs
    ↓
Market Data Service
    ↓
Redis Cache (with TTL)
    ↓
API Endpoints
    ↓
Frontend UI
```

### Caching Strategy
- **OHLCV Data**: 5m - 24h TTL (interval-dependent)
- **Indicators**: 4 hours TTL
- **Prices**: 1 minute TTL
- **Signals**: 30 minutes TTL
- **Portfolio**: 5 minutes TTL

### Symbol Normalization
- **US Stocks**: AAPL, MSFT (no suffix)
- **NSE**: ADANIPORTS.NS, INFY.NS (.NS suffix)
- **BSE**: RELIANCE.BO (.BO suffix)
- **Indices**: ^GSPC, ^NSEI (^ prefix)
- **Crypto**: BTCUSDT, ETHUSDT (USDT suffix)

### Local-First AI
- All ML models trained locally
- Ollama for LLM inference
- No cloud API dependencies
- Reproducible pipelines
- Model artifacts on disk

---

## 🔒 Security Considerations

- Environment variables in `.env` (not committed)
- Database credentials encrypted
- Redis connection authenticated (setup in production)
- API endpoints ready for JWT authentication
- Input validation with Pydantic/Zod
- SQL injection prevention via SQLAlchemy ORM

---

## 📈 Performance Metrics

### API Response Times (Target)
- Market data fetch: < 500ms (cached)
- Indicator calculation: < 200ms
- Portfolio query: < 100ms
- Signal generation: < 500ms

### Scalability
- Database: SQLAlchemy supports connection pooling
- Cache: Redis handles millions of keys
- API: FastAPI async/await for concurrency
- Frontend: Next.js static generation for speed

---

## 🐛 Known Issues & TODOs

- [ ] Rate limiting not yet implemented
- [ ] Batch API requests need optimization
- [ ] WebSocket real-time data streaming
- [ ] Error recovery for Yahoo Finance downtime
- [ ] Database migrations with Alembic
- [ ] Comprehensive test suite
- [ ] Logging and monitoring setup
- [ ] API authentication (currently open)

---

## 📝 Usage Examples

### Get Market Data

```bash
curl "http://localhost:8000/market-data/ohlcv?symbol=AAPL&interval=1d&start_date=2024-01-01"
```

### Calculate RSI Indicator

```bash
curl -X POST "http://localhost:8000/indicators/rsi?symbol=AAPL&period=14"
```

### Get Trading Signals

```bash
curl "http://localhost:8000/indicators/signals/AAPL"
```

### Execute a Trade

```bash
curl -X POST "http://localhost:8000/trading/buy" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "quantity": 10, "price": 189.45}'
```

### Check Portfolio

```bash
curl "http://localhost:8000/trading/portfolio"
```

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete examples.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Create feature branches
5. Submit pull requests

---

## 📄 License

This project is for educational and research purposes.

---

## 📞 Support

- **API Docs (Swagger)**: http://localhost:8000/docs
- **GitHub Issues**: [Create an issue]
- **Documentation**: See `/` root directory `.md` files

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS](https://tailwindcss.com)
- [Trading Technical Analysis](https://en.wikipedia.org/wiki/Technical_analysis)

---

## ⭐ Next Steps

1. ✅ **Backend Complete**: Market data, indicators, trading APIs ready
2. 🔜 **Frontend**: Run `FRONTEND_GUIDE.md` to build Next.js UI
3. 🔜 **AI Layer**: Integrate Ollama for smart analytics
4. 🔜 **Backtesting**: Build historical simulation engine
5. 🔜 **Deploy**: Containerize and deploy to cloud

**Start with:** [SETUP_GUIDE.md](SETUP_GUIDE.md) for backend, [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) for frontend.

---

## 📊 Repository Stats

- **Backend Lines of Code**: ~2,000
- **Core Components**: 9 (trading, market_data, indicators, api, etc.)
- **API Endpoints**: 20+
- **Supported Markets**: 5 (US, NSE, BSE, Crypto, Indices)
- **Technical Indicators**: 8 (SMA, EMA, RSI, MACD, Bollinger, ATR, Stochastic, Support/Resistance)
- **Test Coverage**: [To be added]

---

**Last Updated**: December 2024
**Status**: Production-Grade Backend Ready | Frontend Development Ready


- No real money is used
- No financial advice is provided
- Trading logic is experimental
- Past performance does not imply future results

---

## 🚧 Work in Progress

This project is currently under active development.

Ongoing work includes:

- Expanding trading APIs
- Adding technical indicator calculations
- Integrating AI-powered stock screening
- Improving database design and scalability
- Building a frontend dashboard
- Adding backtesting and strategy evaluation

APIs, schemas, and features may change as the project evolves.

---

## 📌 Future Roadmap

- Multi-user support
- Authentication and authorization
- Advanced AI strategy optimization
- Broker API integrations (optional)
- Enterprise-grade analytics and reporting

---

## 📄 License

This project is currently not licensed for commercial use.
Licensing terms will be added in the future.

---
