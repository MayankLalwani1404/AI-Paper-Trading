# AI Paper Trading Platform - Development Plan

## Current Status
✅ **Backend Infrastructure Complete:**
- FastAPI application with modular structure
- PostgreSQL database with trading models (Account, Position, Trade)
- Redis client configured
- Technical indicators (SMA, EMA, RSI implemented)
- Paper trading business logic (buy/sell)
- Basic API endpoints (/trading/buy, /trading/sell, /trading/portfolio)
- Configuration management via Pydantic Settings
- Ollama integration prepared in config

✅ **Datasets Available:**
- AAPL_historical.csv
- ADANIPORTS.csv
- BTCUSDT_5m_2017-09-01_to_2025-09-23.csv
- historical_stock_prices.csv
- ohlc.csv

✅ **.gitignore Already Configured:**
- datasets/ folder already in .gitignore to prevent uploads

---

## Phase 1: Market Data Ingestion & Caching Layer
**Priority: HIGH | Status: IN PROGRESS**

### 1.1 Market Data Service
- [ ] Create `backend/market_data/service.py`
  - Yahoo Finance integration with yfinance
  - Local CSV fallback loader
  - Symbol normalization (US: no suffix, NSE: .NS, BSE: .BO, indices: ^SYMBOL)
- [ ] Create `backend/market_data/cache.py`
  - Redis caching layer with TTL policies
  - Cache key strategies by symbol, interval, date range
  - Automatic expiration for intraday data (shorter TTL)

### 1.2 Symbol Registry & Metadata
- [ ] Create `backend/market_data/symbols.py`
  - Symbol metadata mapping (market, sector, etc.)
  - Symbol validation and normalization
  - Support for US stocks, NSE, BSE, crypto

### 1.3 Market Data API Endpoints
- [ ] `GET /market-data/ohlcv?symbol=AAPL&interval=1d&start=YYYY-MM-DD&end=YYYY-MM-DD`
- [ ] `GET /market-data/latest?symbol=AAPL`
- [ ] `GET /market-data/symbols` - List available symbols

---

## Phase 2: Indicator Calculation APIs
**Priority: HIGH | Status: PENDING**

### 2.1 Indicator Service Enhancement
- [ ] Create `backend/indicators/service.py`
  - Extend technical indicators with full suite (MACD, Bollinger Bands, ATR, Stochastic)
  - Use Redis-cached OHLCV data
  - Return structured responses

### 2.2 Indicator API Endpoints
- [ ] `POST /indicators/calculate` - Calculate indicators for a symbol
- [ ] `GET /indicators/available` - List all available indicators
- [ ] `POST /indicators/signal` - Compute buy/sell signals from indicators

### 2.3 Database Models for Indicator Results
- [ ] Add `IndicatorResult` model to store indicator cache/history
- [ ] Track when indicators were calculated for optimization

---

## Phase 3: Frontend Application (Next.js + TypeScript)
**Priority: HIGH | Status: PENDING**

### 3.1 Project Setup
- [ ] Create Next.js project in `frontend/`
- [ ] Configure TypeScript, TailwindCSS, ESLint
- [ ] Setup API client with Axios or fetch wrapper
- [ ] Configure authentication (initially mocked/simplified)

### 3.2 Core Pages & Components
- [ ] Dashboard page with portfolio overview
- [ ] Portfolio page (positions, P&L, trade history)
- [ ] Market scanner / stock search page
- [ ] Trading page (buy/sell forms with simulation)
- [ ] Charts page (TradingView Lightweight Charts)
- [ ] AI Insights page (placeholder for Phase 4)

### 3.3 UI/UX Components
- [ ] Responsive layout with navigation
- [ ] Real-time price ticker / watchlist
- [ ] Portfolio cards and metrics
- [ ] Trade execution forms with confirmation
- [ ] Chart display with technical overlays

---

## Phase 4: AI Integration & Decision Support
**Priority: MEDIUM | Status: PENDING**

### 4.1 Ollama Integration
- [ ] Create `backend/ai/llm.py`
  - Ollama client wrapper
  - Prompt templates for stock analysis
  - Natural-language query to structured filters

### 4.2 Pattern Recognition
- [ ] Create `backend/ai/patterns.py`
  - Train/load local models for chart patterns
  - Candlestick pattern detection
  - Support/Resistance level identification

### 4.3 Trade Signal Generation
- [ ] Create `backend/ai/signals.py`
  - Combine indicators + patterns + LLM insights
  - Score trade setups
  - Return explainable recommendations

### 4.4 AI API Endpoints
- [ ] `POST /ai/analyze-stock` - Full analysis with indicators + patterns
- [ ] `POST /ai/search` - Natural-language stock search
- [ ] `POST /ai/recommend-trades` - Get AI trade recommendations
- [ ] `GET /ai/insights` - Latest market insights

---

## Phase 5: Strategy & Backtesting
**Priority: MEDIUM | Status: PENDING**

### 5.1 Strategy Framework
- [ ] Create `backend/strategies/base.py` - Abstract strategy class
- [ ] Create `backend/strategies/models.py` - DB models for stored strategies
- [ ] Implement simple strategies (RSI-based, SMA crossover, etc.)

### 5.2 Backtesting Engine
- [ ] Create `backend/backtesting/engine.py`
  - Load historical OHLCV data
  - Simulate strategy execution
  - Calculate returns, Sharpe ratio, max drawdown

### 5.3 Backtesting API
- [ ] `POST /backtesting/run` - Run strategy against historical data
- [ ] `GET /backtesting/results/{test_id}` - Get backtest results

---

## Phase 6: Advanced Features (Future)
**Priority: LOW | Status: PENDING**

- [ ] Multi-user authentication with JWT
- [ ] User profiles and preferences
- [ ] Real-time WebSocket updates
- [ ] Paper trading leaderboards
- [ ] Email/Slack alerts for trade signals
- [ ] Export portfolio data
- [ ] Mobile app support

---

## Database Schema Evolution

### Current Models:
- Account (id, balance, created_at)
- Position (id, symbol, quantity, avg_price, account_id, created_at)
- Trade (id, symbol, quantity, price, side, account_id, created_at)

### Planned Additions:
- IndicatorResult (symbol, indicator_name, values, calculated_at, expires_at)
- Strategy (name, rules, created_at, updated_at)
- BacktestResult (strategy_id, start_date, end_date, returns, sharpe, max_dd)
- User (for multi-user support)
- AIInsight (symbol, insight_type, text, score, created_at)

---

## Redis Cache Strategy

| Key Pattern | TTL | Purpose |
|---|---|---|
| `ohlcv:{symbol}:{interval}:{date}` | 1-24h (interval-dependent) | Market data |
| `indicators:{symbol}:{name}:{date}` | 4h | Calculated indicators |
| `latest_price:{symbol}` | 1m | Real-time prices |
| `portfolio:{account_id}` | 5m | Portfolio cache |
| `signals:{symbol}` | 30m | Trade signals |

---

## Environment Variables (Already Configured)
```
DATABASE_URL=postgresql://papertrader:papertraderpass@localhost:5432/papertrading
REDIS_URL=redis://localhost:6379
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Next Immediate Steps
1. **This Session:**
   - ✅ Gitignore verified for datasets/
   - Build market data service with Yahoo Finance + local fallback
   - Implement Redis caching layer
   - Create market data API endpoints
   - Extend indicator endpoints

2. **Following Session:**
   - Build Next.js frontend with core pages
   - Connect frontend to backend APIs
   - Add portfolio visualization

3. **Subsequent Sessions:**
   - Ollama integration for NLP
   - Pattern recognition models
   - Backtesting engine
   - Advanced AI features

---

## Success Metrics
- ✅ Backend serves real market data via REST API
- ✅ Frontend displays portfolio and enables trading simulation
- ✅ Indicators calculate and cache properly
- ✅ AI can translate natural language to filters
- ✅ Backtesting validates strategy performance
- ✅ System scales to multiple users (architecture ready)
