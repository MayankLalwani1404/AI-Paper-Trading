import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Market Data API
export const marketDataAPI = {
  getSymbols: (market?: string) => 
    api.get('/market-data/symbols', { params: { market } }),
  
  getLatestPrice: (symbol: string) =>
    api.get('/market-data/latest-price', { params: { symbol } }),
  
  getMultiplePrices: (symbols: string[]) =>
    api.get('/market-data/multiple-prices', { params: { symbols: symbols.join(',') } }),
  
  getOHLCV: (symbol: string, interval: string = '1d', startDate?: string, endDate?: string) =>
    api.get('/market-data/ohlcv', { 
      params: { symbol, interval, start_date: startDate, end_date: endDate } 
    }),
  
  searchSymbols: (query: string) =>
    api.get('/market-data/search', { params: { q: query } }),
};

// Indicators API
export const indicatorsAPI = {
  getAvailableIndicators: () =>
    api.get('/indicators/available'),
  
  calculateIndicator: (symbol: string, indicator: string, params?: any) =>
    api.post('/indicators/calculate', { symbol, indicator, ...params }),
  
  getAllIndicators: (symbol: string, period?: number) =>
    api.get('/indicators/all', { params: { symbol, period } }),
  
  getTradeSignals: (symbol: string) =>
    api.get('/indicators/signals', { params: { symbol } }),
};

// Trading API
export const tradingAPI = {
  getPortfolio: () =>
    api.get('/trading/portfolio'),
  
  placeOrder: (data: any) =>
    api.post('/trading/order', data),
  
  getPositions: () =>
    api.get('/trading/positions'),
  
  getTrades: () =>
    api.get('/trading/trades'),
  
  getOrders: () =>
    api.get('/trading/orders'),
  
  createWatchlist: (name: string) =>
    api.post('/trading/watchlists', { name }),
  
  getWatchlists: () =>
    api.get('/trading/watchlists'),
  
  addWatchlistItem: (watchlistId: number, symbol: string) =>
    api.post(`/trading/watchlists/${watchlistId}/items`, { symbol }),
  
  removeWatchlistItem: (watchlistId: number, symbol: string) =>
    api.delete(`/trading/watchlists/${watchlistId}/items/${symbol}`),
};

// AI API
export const aiAPI = {
  filter: (query: string, market?: string, limit: number = 25) =>
    api.post('/ai/filter', { query, market, limit }),
  
  patterns: (symbol: string, holdingPeriod?: string) =>
    api.post('/ai/patterns', { symbol, holding_period: holdingPeriod }),
};

// Health check
export const healthAPI = {
  check: () =>
    api.get('/health'),
};

export default api;
