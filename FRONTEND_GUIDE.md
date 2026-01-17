# Frontend Development Guide - Next.js + TypeScript

## Overview

The frontend is a modern, responsive web application built with:
- **Next.js 14**: React framework for production
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling
- **SWR/React Query**: Data fetching and caching
- **Chart.js / TradingView Charts**: Financial charting
- **Zod**: Type-safe schema validation

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── _app.tsx              # App wrapper, providers
│   │   ├── _document.tsx         # HTML document setup
│   │   ├── index.tsx             # Dashboard home
│   │   ├── portfolio.tsx         # Portfolio view
│   │   ├── market-scanner.tsx    # Stock scanner
│   │   ├── trading.tsx           # Trade execution
│   │   ├── charts.tsx            # Advanced charting
│   │   ├── ai-insights.tsx       # AI analysis results
│   │   └── api/
│   │       └── [proxy].ts        # API proxy (optional)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── portfolio/
│   │   │   ├── PortfolioCard.tsx
│   │   │   ├── PositionsList.tsx
│   │   │   └── PerformanceMetrics.tsx
│   │   ├── trading/
│   │   │   ├── BuyForm.tsx
│   │   │   ├── SellForm.tsx
│   │   │   └── OrderHistory.tsx
│   │   ├── charts/
│   │   │   ├── CandleChart.tsx
│   │   │   ├── IndicatorOverlay.tsx
│   │   │   └── SignalDisplay.tsx
│   │   ├── scanner/
│   │   │   ├── SymbolSearch.tsx
│   │   │   ├── ResultsTable.tsx
│   │   │   └── QuickStats.tsx
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loading.tsx
│   │   └── ai/
│   │       ├── InsightsPanel.tsx
│   │       ├── SignalScore.tsx
│   │       └── RecommendationBadge.tsx
│   ├── lib/
│   │   ├── api.ts               # API client wrapper
│   │   ├── hooks/
│   │   │   ├── useMarketData.ts
│   │   │   ├── usePortfolio.ts
│   │   │   ├── useIndicators.ts
│   │   │   └── useSignals.ts
│   │   ├── types/
│   │   │   ├── api.ts           # API response types
│   │   │   ├── market.ts        # Market data types
│   │   │   └── trading.ts       # Trading types
│   │   ├── utils/
│   │   │   ├── format.ts        # Number/date formatting
│   │   │   ├── calculations.ts  # P&L calculations
│   │   │   └── validators.ts    # Form validation
│   │   └── constants.ts         # App constants
│   ├── styles/
│   │   ├── globals.css
│   │   └── variables.css
│   └── context/
│       ├── AuthContext.tsx
│       └── ThemeContext.tsx
├── public/
│   ├── favicon.ico
│   └── assets/
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
├── .env.local
└── README.md
```

## Setup Instructions

### 1. Create Next.js Project

```bash
# From project root
cd frontend

# Create Next.js app with TypeScript
npx create-next-app@latest . --typescript --tailwind --eslint

# Or if starting fresh:
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --src-dir
```

### 2. Install Dependencies

```bash
cd frontend

npm install

# Additional packages
npm install \
  axios \
  swr \
  react-query \
  zod \
  chart.js \
  react-chartjs-2 \
  lightweight-charts \
  lucide-react \
  clsx \
  date-fns

# Dev dependencies
npm install --save-dev \
  @types/node \
  @types/react \
  @types/chart.js \
  prettier \
  tailwindcss-forms
```

### 3. Configuration Files

#### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@pages/*": ["src/pages/*"],
      "@lib/*": ["src/lib/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### `tailwind.config.js`

```js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1f2937',
        secondary: '#10b981',
        danger: '#ef4444',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
};
```

#### `next.config.js`

```js
module.exports = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  rewrites: async () => {
    return {
      fallback: [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
        },
      ],
    };
  },
};
```

### 4. Environment Setup

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Paper Trading Platform
```

## Core Components

### API Client (`src/lib/api.ts`)

```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Market Data
export const marketDataAPI = {
  getOHLCV: (symbol: string, interval: string = '1d') =>
    api.get(`/market-data/ohlcv`, { params: { symbol, interval } }),
  
  getLatestPrice: (symbol: string) =>
    api.get(`/market-data/latest-price`, { params: { symbol } }),
  
  searchSymbols: (query: string) =>
    api.get(`/market-data/search`, { params: { query } }),
};

// Indicators
export const indicatorsAPI = {
  calculate: (symbol: string, indicator: string, params = {}) =>
    api.post(`/indicators/calculate`, null, { params: { symbol, indicator, ...params } }),
  
  getSignals: (symbol: string) =>
    api.get(`/indicators/signals/${symbol}`),
};

// Trading
export const tradingAPI = {
  buy: (symbol: string, quantity: number, price: number) =>
    api.post(`/trading/buy`, { symbol, quantity, price }),
  
  sell: (symbol: string, quantity: number, price: number) =>
    api.post(`/trading/sell`, { symbol, quantity, price }),
  
  getPortfolio: () =>
    api.get(`/trading/portfolio`),
};
```

### Custom Hooks

#### `src/lib/hooks/useMarketData.ts`

```typescript
import useSWR from 'swr';
import { marketDataAPI } from '@lib/api';

export function useMarketData(symbol: string, interval: string = '1d') {
  const { data, error, isLoading } = useSWR(
    symbol ? [`/market-data/ohlcv`, symbol, interval] : null,
    () => marketDataAPI.getOHLCV(symbol, interval)
  );

  return {
    data: data?.data,
    isLoading,
    error,
  };
}

export function useLatestPrice(symbol: string) {
  const { data, error, isLoading, mutate } = useSWR(
    symbol ? `/market-data/price/${symbol}` : null,
    () => marketDataAPI.getLatestPrice(symbol),
    { refreshInterval: 60000 } // Refresh every minute
  );

  return {
    price: data?.data?.price,
    isLoading,
    error,
    refetch: mutate,
  };
}
```

#### `src/lib/hooks/usePortfolio.ts`

```typescript
import useSWR from 'swr';
import { tradingAPI } from '@lib/api';

export function usePortfolio() {
  const { data, error, isLoading, mutate } = useSWR(
    '/trading/portfolio',
    tradingAPI.getPortfolio,
    { refreshInterval: 30000 } // Refresh every 30 seconds
  );

  return {
    portfolio: data?.data,
    isLoading,
    error,
    refetch: mutate,
  };
}
```

#### `src/lib/hooks/useIndicators.ts`

```typescript
import useSWR from 'swr';
import { indicatorsAPI } from '@lib/api';

export function useIndicators(symbol: string) {
  const { data, error, isLoading } = useSWR(
    symbol ? [`/indicators`, symbol] : null,
    () => indicatorsAPI.calculate(symbol, 'RSI')
  );

  return {
    indicators: data?.data,
    isLoading,
    error,
  };
}

export function useSignals(symbol: string) {
  const { data, error, isLoading, mutate } = useSWR(
    symbol ? [`/indicators/signals`, symbol] : null,
    () => indicatorsAPI.getSignals(symbol),
    { refreshInterval: 300000 } // Refresh every 5 minutes
  );

  return {
    signals: data?.data,
    isLoading,
    error,
    refetch: mutate,
  };
}
```

## Page Templates

### Dashboard (`src/pages/index.tsx`)

```typescript
import Layout from '@components/layout/Layout';
import PortfolioOverview from '@components/portfolio/PortfolioOverview';
import MarketTicker from '@components/common/MarketTicker';
import RecentTrades from '@components/trading/RecentTrades';

export default function Dashboard() {
  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PortfolioOverview />
        </div>
        <div>
          <MarketTicker />
        </div>
      </div>
      <div className="mt-6">
        <RecentTrades />
      </div>
    </Layout>
  );
}
```

### Trading Page (`src/pages/trading.tsx`)

```typescript
import { useState } from 'react';
import Layout from '@components/layout/Layout';
import SymbolSearch from '@components/scanner/SymbolSearch';
import BuyForm from '@components/trading/BuyForm';
import SellForm from '@components/trading/SellForm';
import OrderHistory from '@components/trading/OrderHistory';
import SignalDisplay from '@components/charts/SignalDisplay';
import { useLatestPrice, useSignals } from '@lib/hooks';

export default function Trading() {
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  
  const { price } = useLatestPrice(selectedSymbol);
  const { signals } = useSignals(selectedSymbol);

  return (
    <Layout>
      <div className="space-y-6">
        <SymbolSearch onSelect={setSelectedSymbol} />
        
        {selectedSymbol && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {signals && <SignalDisplay signals={signals} />}
            </div>
            <div className="space-y-4">
              {price && <BuyForm symbol={selectedSymbol} currentPrice={price} />}
              {price && <SellForm symbol={selectedSymbol} currentPrice={price} />}
            </div>
          </div>
        )}
        
        <OrderHistory />
      </div>
    </Layout>
  );
}
```

### Market Scanner (`src/pages/market-scanner.tsx`)

```typescript
import { useState } from 'react';
import Layout from '@components/layout/Layout';
import SymbolSearch from '@components/scanner/SymbolSearch';
import ResultsTable from '@components/scanner/ResultsTable';
import QuickStats from '@components/scanner/QuickStats';

export default function MarketScanner() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [filters, setFilters] = useState({
    market: 'US',
    sector: '',
    minPrice: 0,
    maxPrice: Infinity,
  });

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Market Scanner</h1>
        
        <SymbolSearch onSearch={setSymbols} />
        
        {symbols.length > 0 && (
          <div className="space-y-4">
            <QuickStats symbols={symbols} />
            <ResultsTable symbols={symbols} />
          </div>
        )}
      </div>
    </Layout>
  );
}
```

## Component Examples

### PortfolioCard Component

```typescript
interface PortfolioCardProps {
  balance: number;
  invested: number;
  totalValue: number;
  pnl: number;
  pnlPercent: number;
}

export default function PortfolioCard({
  balance,
  invested,
  totalValue,
  pnl,
  pnlPercent,
}: PortfolioCardProps) {
  const isProfitable = pnl >= 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Portfolio Overview</h2>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-gray-600 text-sm">Cash Balance</p>
          <p className="text-2xl font-bold">${balance.toFixed(2)}</p>
        </div>
        
        <div>
          <p className="text-gray-600 text-sm">Invested</p>
          <p className="text-2xl font-bold">${invested.toFixed(2)}</p>
        </div>
        
        <div>
          <p className="text-gray-600 text-sm">Total Value</p>
          <p className="text-2xl font-bold">${totalValue.toFixed(2)}</p>
        </div>
        
        <div>
          <p className="text-gray-600 text-sm">P&L</p>
          <p className={`text-2xl font-bold ${isProfitable ? 'text-green-600' : 'text-red-600'}`}>
            ${pnl.toFixed(2)} ({pnlPercent.toFixed(2)}%)
          </p>
        </div>
      </div>
    </div>
  );
}
```

## Development Workflow

### Running Development Server

```bash
cd frontend
npm run dev

# Open http://localhost:3000
```

### Building for Production

```bash
npm run build
npm run start
```

### Code Quality

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check
```

## Styling Strategy

Use TailwindCSS with custom theme:

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
}
```

## Features Roadmap

### Phase 1: MVP (Weeks 1-2)
- [x] Project setup
- [ ] Portfolio dashboard
- [ ] Buy/sell forms
- [ ] Price display
- [ ] Basic charting

### Phase 2: Enhanced (Weeks 3-4)
- [ ] Advanced charting with TradingView
- [ ] Indicators visualization
- [ ] Signal display
- [ ] Trade history
- [ ] Search and filtering

### Phase 3: AI Integration (Weeks 5-6)
- [ ] AI insights panel
- [ ] Pattern recognition display
- [ ] Signal scoring
- [ ] Recommendation engine

### Phase 4: Polish (Week 7-8)
- [ ] Authentication
- [ ] Dark mode
- [ ] Mobile responsiveness
- [ ] Performance optimization
- [ ] Error handling

## Next Steps

1. Initialize Next.js project
2. Install dependencies
3. Setup API client and hooks
4. Create page layouts
5. Build components
6. Connect to backend API
7. Add real-time updates with WebSockets
8. Deploy to Vercel or self-hosted

---

For more information, see:
- [API Documentation](API_DOCUMENTATION.md)
- [Backend Setup](SETUP_GUIDE.md)
