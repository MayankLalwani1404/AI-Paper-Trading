# AI Paper Trading - Frontend

Production-grade Next.js frontend for the AI-powered paper trading platform.

## Features

- **Dashboard**: Portfolio overview, cash balance, open positions
- **Portfolio**: Detailed holdings with gain/loss tracking
- **Market Scanner**: Real-time technical indicators and trading signals
- **Charts**: Interactive price charts with multiple intervals
- **Trading**: Place buy/sell orders with order validation
- **Live Updates**: Real-time data using SWR with 5s-60s refresh intervals

## Tech Stack

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Data Fetching**: SWR + Axios
- **Charts**: Recharts
- **Icons**: Lucide React
- **Date Handling**: date-fns

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx          # Dashboard
│   │   ├── portfolio/page.tsx # Portfolio page
│   │   ├── market/page.tsx    # Market scanner
│   │   ├── charts/page.tsx    # Charts
│   │   ├── trading/page.tsx   # Trading interface
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── Sidebar.tsx        # Navigation sidebar
│   │   ├── SignalCard.tsx     # Trading signals display
│   │   └── PriceChart.tsx     # OHLCV chart component
│   └── lib/
│       ├── api.ts            # API client
│       └── hooks.ts          # Custom data hooks
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── run_frontend.sh
```

## Installation

```bash
cd frontend
npm install
```

## Environment Variables

The frontend looks for the backend at `http://localhost:8000` by default.
To change this, create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running

### Development Mode

```bash
cd frontend
bash run_frontend.sh
```

Frontend will be available at `http://localhost:3000`

### Production Build

```bash
cd frontend
npm run build
npm start
```

## API Endpoints

The frontend connects to these backend endpoints:

### Market Data
- `GET /market-data/symbols` - Get available symbols
- `GET /market-data/latest-price?symbol=AAPL` - Get latest price
- `GET /market-data/ohlcv?symbol=AAPL&interval=1d` - Get OHLCV data

### Indicators
- `GET /indicators/available` - Get available indicators
- `POST /indicators/calculate` - Calculate indicator
- `GET /indicators/signals?symbol=AAPL` - Get trade signals

### Trading
- `GET /trading/portfolio` - Get portfolio
- `POST /trading/order` - Place order
- `GET /trading/positions` - Get open positions

## Custom Hooks

- `useLatestPrice(symbol)` - Fetch latest price (5s refresh)
- `useOHLCV(symbol, interval)` - Fetch OHLCV data (60s refresh)
- `useTradeSignals(symbol)` - Fetch trade signals (30s refresh)
- `useIndicators(symbol)` - Fetch all indicators (60s refresh)
- `usePortfolio()` - Fetch portfolio data (10s refresh)
- `useSymbols(market)` - Fetch available symbols

## Pages

### Dashboard (`/`)
- Portfolio value overview
- Cash balance display
- Open positions list
- Quick action buttons

### Portfolio (`/portfolio`)
- Detailed holdings table
- Entry price vs current price
- Gain/loss tracking
- Return percentage

### Market Scanner (`/market`)
- Symbol selection
- Real-time trading signals
- Technical indicators grid
- AI recommendation

### Charts (`/charts`)
- Symbol selector
- Interval selector (1m, 5m, 1h, 1d, 1w)
- Interactive price chart
- Open/Close/High/Low lines

### Trading (`/trading`)
- Order form (BUY/SELL)
- Quantity and price input
- Order summary
- Order confirmation

## Testing

Test both frontend and backend together:

```bash
# In project root
bash test_full_stack.sh
```

This will verify:
- Backend API health
- Market data endpoints
- Indicators endpoints
- Trading endpoints
- Frontend connectivity

## Running Fullstack

Start both frontend and backend with one command:

```bash
# In project root
bash run_all.sh
```

Or in separate terminals:

```bash
# Terminal 1 - Backend
cd backend
bash run_backend.sh

# Terminal 2 - Frontend
cd frontend
bash run_frontend.sh
```

## Development Notes

- The frontend auto-refreshes on code changes (Next.js hot reload)
- API responses are cached by SWR to minimize requests
- All prices are formatted to 2 decimal places
- Real-time updates use configurable refresh intervals
- Error handling is implemented on all data fetches
- Forms include validation and error feedback

## Troubleshooting

**"Cannot connect to backend"**
- Ensure backend is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

**"Symbols not loading"**
- Verify market data endpoint: `curl http://localhost:8000/market-data/symbols`

**"Charts not displaying"**
- Check browser console for errors
- Ensure OHLCV data is available for the selected symbol

**Port already in use**
- Frontend runs on 3000, Backend on 8000
- Change ports in run scripts if needed
