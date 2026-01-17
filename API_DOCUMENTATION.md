# API Documentation - AI Paper Trading Platform

## Overview

The Paper Trading Backend provides a comprehensive REST API for:
- Paper trading (simulated stock trading)
- Market data access (OHLCV from Yahoo Finance or local datasets)
- Technical indicator calculation
- Trading signal generation
- Portfolio management

**Base URL**: `http://localhost:8000`

---

## Table of Contents

1. [Health Check](#health-check)
2. [Market Data APIs](#market-data-apis)
3. [Indicator APIs](#indicator-apis)
4. [Trading APIs](#trading-apis)
5. [Error Handling](#error-handling)

---

## Health Check

### `GET /health`
Check if the backend is running.

**Response:**
```json
{
  "status": "ok",
  "message": "Paper Trading Backend is running"
}
```

---

## Market Data APIs

### `GET /market-data/ohlcv`

Fetch OHLCV (candlestick) data for a symbol.

**Query Parameters:**
- `symbol` (required): Trading symbol (e.g., AAPL, ADANIPORTS.NS)
- `interval` (optional, default="1d"): Candle interval
  - Options: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`, `1mo`
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Example Request:**
```bash
GET http://localhost:8000/market-data/ohlcv?symbol=AAPL&interval=1d&start_date=2024-01-01&end_date=2024-12-31
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "data": [
    {
      "date": "2024-01-01T00:00:00",
      "open": 185.50,
      "high": 186.25,
      "low": 185.00,
      "close": 185.75,
      "volume": 1000000
    },
    ...
  ],
  "count": 250
}
```

---

### `GET /market-data/latest-price`

Get the latest available price for a symbol.

**Query Parameters:**
- `symbol` (required): Trading symbol

**Example Request:**
```bash
GET http://localhost:8000/market-data/latest-price?symbol=AAPL
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "price": 189.45
}
```

---

### `POST /market-data/prices`

Get latest prices for multiple symbols in a single request.

**Request Body:**
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"]
}
```

**Example Response:**
```json
{
  "prices": {
    "AAPL": 189.45,
    "MSFT": 378.91,
    "GOOGL": 140.22
  }
}
```

---

### `GET /market-data/search`

Search for symbols by name or ticker.

**Query Parameters:**
- `query` (required): Search query (e.g., "Apple", "AAPL")

**Example Request:**
```bash
GET http://localhost:8000/market-data/search?query=Apple
```

**Example Response:**
```json
{
  "query": "Apple",
  "results": ["AAPL"],
  "count": 1
}
```

---

### `GET /market-data/symbols`

Get list of available symbols, optionally filtered by market.

**Query Parameters:**
- `market` (optional): Market filter
  - Options: `US`, `NSE`, `BSE`, `CRYPTO`, `INDEX`

**Example Request:**
```bash
GET http://localhost:8000/market-data/symbols?market=US
```

**Example Response:**
```json
{
  "market": "US",
  "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
  "count": 5
}
```

---

### `GET /market-data/symbols/by-market`

Get all symbols grouped by market.

**Example Response:**
```json
{
  "markets": {
    "US": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "NSE": ["ADANIPORTS.NS", "INFY.NS", "TCS.NS"],
    "BSE": [],
    "CRYPTO": ["BTCUSDT", "ETHUSDT"],
    "INDEX": ["^GSPC", "^NSEI"]
  }
}
```

---

### `POST /market-data/validate-symbol`

Validate if a symbol is supported.

**Query Parameters:**
- `symbol` (required): Trading symbol

**Example Request:**
```bash
POST http://localhost:8000/market-data/validate-symbol?symbol=AAPL
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "valid": true
}
```

---

### `GET /market-data/info/{symbol}`

Get metadata information for a symbol.

**Path Parameters:**
- `symbol` (required): Trading symbol

**Example Request:**
```bash
GET http://localhost:8000/market-data/info/AAPL
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "market": "US",
  "name": "Apple Inc.",
  "sector": "Technology",
  "country": "US",
  "registered": true
}
```

---

## Indicator APIs

### `GET /indicators/available`

Get list of all available technical indicators.

**Example Response:**
```json
{
  "indicators": [
    {
      "name": "SMA",
      "label": "Simple Moving Average",
      "default_params": 20
    },
    {
      "name": "EMA",
      "label": "Exponential Moving Average",
      "default_params": 20
    },
    {
      "name": "RSI",
      "label": "Relative Strength Index",
      "default_params": 14
    },
    ...
  ],
  "count": 8
}
```

---

### `POST /indicators/calculate`

Calculate a specific indicator for a symbol.

**Query Parameters:**
- `symbol` (required): Trading symbol
- `indicator` (required): Indicator name (SMA, EMA, RSI, MACD, BOLLINGER, ATR, STOCHASTIC, SUPPORT_RESISTANCE)
- `period` (optional): Period for SMA, EMA, RSI, ATR, BOLLINGER, SUPPORT_RESISTANCE
- `fast`, `slow`, `signal_period` (optional): Parameters for MACD
- `std_dev` (optional): Standard deviation for Bollinger Bands (default: 2.0)
- `smooth` (optional): Smoothing period for Stochastic (default: 3)

**Example Request:**
```bash
POST http://localhost:8000/indicators/calculate?symbol=AAPL&indicator=RSI&period=14
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "indicator": "RSI",
  "values": [null, null, ..., 65.42, 63.28, 61.15],
  "metadata": {
    "period": 14,
    "overbought": 70,
    "oversold": 30
  }
}
```

---

### `GET /indicators/all/{symbol}`

Calculate all available indicators for a symbol.

**Path Parameters:**
- `symbol` (required): Trading symbol

**Example Request:**
```bash
GET http://localhost:8000/indicators/all/AAPL
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "last_price": 189.45,
  "indicators": {
    "SMA": {
      "symbol": "AAPL",
      "indicator": "SMA",
      "values": [...],
      "metadata": {"period": 20}
    },
    "EMA": {...},
    "RSI": {...},
    ...
  }
}
```

---

### `GET /indicators/signals/{symbol}`

Generate trading signals for a symbol based on multiple indicators.

**Path Parameters:**
- `symbol` (required): Trading symbol

**Example Request:**
```bash
GET http://localhost:8000/indicators/signals/AAPL
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "timestamp": "2024-12-31T16:00:00",
  "current_price": 189.45,
  "buy_signals": [
    "SMA 20 > SMA 50 (Bullish Trend)",
    "Near Support (185.50)"
  ],
  "sell_signals": [],
  "neutral_indicators": [
    "RSI: 55.42"
  ],
  "score": 35,
  "recommendation": "BUY"
}
```

---

### Convenience Indicator Endpoints

**Quick endpoints for common indicators:**

- `POST /indicators/sma?symbol=AAPL&period=20`
- `POST /indicators/ema?symbol=AAPL&period=20`
- `POST /indicators/rsi?symbol=AAPL&period=14`
- `POST /indicators/macd?symbol=AAPL&fast=12&slow=26&signal_period=9`
- `POST /indicators/bollinger?symbol=AAPL&period=20&std_dev=2.0`
- `POST /indicators/atr?symbol=AAPL&period=14`
- `POST /indicators/stochastic?symbol=AAPL&period=14&smooth=3`

---

## Trading APIs

### `POST /trading/buy`

Simulate a buy order.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "quantity": 10,
  "price": 189.45
}
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "quantity": 10,
  "price": 189.45,
  "side": "BUY",
  "balance": 812745.50
}
```

---

### `POST /trading/sell`

Simulate a sell order.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "quantity": 5,
  "price": 190.00
}
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "quantity": 5,
  "price": 190.00,
  "side": "SELL",
  "balance": 813695.50
}
```

---

### `GET /trading/portfolio`

Get current portfolio status.

**Example Response:**
```json
{
  "account_id": 1,
  "balance": 813695.50,
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 5,
      "avg_price": 189.45,
      "current_price": 190.00,
      "unrealized_pnl": 2.75,
      "unrealized_pnl_percent": 0.29
    }
  ],
  "total_value": 814695.50,
  "cash": 813695.50,
  "invested": 1000.00
}
```

---

## Error Handling

All errors are returned in a standard JSON format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters or data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Example Error Response:**
```json
{
  "detail": "No data found for INVALID_SYMBOL"
}
```

---

## Caching

The backend automatically caches:
- OHLCV data (TTL based on interval: 5m for intraday, 24h for daily)
- Indicator calculations (TTL: 4 hours)
- Price data (TTL: 1 minute)
- Trade signals (TTL: 30 minutes)

Cache is stored in Redis and automatically managed. You can force fresh data by using the backend directly without cache.

---

## Rate Limiting & Performance Notes

- No rate limiting currently implemented (add as needed for production)
- Market data is fetched from Yahoo Finance or local CSV files
- Indicators are calculated in-memory for performance
- Large date ranges may take longer to fetch and calculate

---

## Data Sources

### Market Data Sources (in priority order):
1. Yahoo Finance API (online)
2. Local CSV datasets in `/datasets/` folder (offline)

### Supported Markets:
- **US**: NYSE/NASDAQ stocks
- **NSE**: National Stock Exchange (India) - use `.NS` suffix
- **BSE**: Bombay Stock Exchange (India) - use `.BO` suffix
- **CRYPTO**: Cryptocurrencies (Bitcoin, Ethereum, etc.)
- **INDEX**: Market indices (S&P 500, NIFTY 50, etc.)

---

## Example Workflows

### Workflow 1: Get Data and Calculate Indicators

```bash
# 1. Get OHLCV data
curl "http://localhost:8000/market-data/ohlcv?symbol=AAPL&interval=1d"

# 2. Calculate RSI
curl -X POST "http://localhost:8000/indicators/rsi?symbol=AAPL&period=14"

# 3. Get trading signals
curl "http://localhost:8000/indicators/signals/AAPL"
```

### Workflow 2: Execute a Trade

```bash
# 1. Get latest price
curl "http://localhost:8000/market-data/latest-price?symbol=AAPL"

# 2. Buy stocks
curl -X POST "http://localhost:8000/trading/buy" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "quantity": 10, "price": 189.45}'

# 3. Check portfolio
curl "http://localhost:8000/trading/portfolio"
```

### Workflow 3: Multi-Symbol Analysis

```bash
# 1. Search for stocks
curl "http://localhost:8000/market-data/search?query=tech"

# 2. Get prices
curl -X POST "http://localhost:8000/market-data/prices" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"]}'

# 3. Analyze all with indicators
for symbol in AAPL MSFT GOOGL; do
  curl "http://localhost:8000/indicators/signals/$symbol"
done
```

---

## Next Features (Planned)

- [ ] AI-powered stock screening (via Ollama)
- [ ] Backtesting engine
- [ ] Strategy management
- [ ] WebSocket real-time updates
- [ ] Multi-user authentication
- [ ] Paper trading leaderboard

