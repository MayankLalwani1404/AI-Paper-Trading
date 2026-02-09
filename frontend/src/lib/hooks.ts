import useSWR from 'swr';
import api, { marketDataAPI, indicatorsAPI, tradingAPI } from './api';

const fetcher = (url: string) => api.get(url).then(res => res.data);

// Hook for latest price
export const useLatestPrice = (symbol?: string) => {
  const { data, error, isLoading } = useSWR(
    symbol ? `/market-data/latest-price?symbol=${symbol}` : null,
    fetcher,
    { refreshInterval: 5000 } // Refresh every 5 seconds
  );

  return {
    price: data?.price,
    timestamp: data?.timestamp,
    error,
    isLoading,
  };
};

// Hook for OHLCV data
export const useOHLCV = (symbol?: string, interval: string = '1d') => {
  const { data, error, isLoading } = useSWR(
    symbol ? `/market-data/ohlcv?symbol=${symbol}&interval=${interval}` : null,
    fetcher,
    { refreshInterval: 60000 } // Refresh every minute
  );

  return {
    data: data?.data || [],
    error,
    isLoading,
  };
};

// Hook for trade signals
export const useTradeSignals = (symbol?: string) => {
  const { data, error, isLoading } = useSWR(
    symbol ? `/indicators/signals/${symbol}` : null,
    fetcher,
    { refreshInterval: 30000 } // Refresh every 30 seconds
  );

  return {
    signals: data?.signals,
    score: data?.score,
    recommendation: data?.recommendation,
    error,
    isLoading,
  };
};

// Hook for all indicators
export const useIndicators = (symbol?: string) => {
  const { data, error, isLoading } = useSWR(
    symbol ? `/indicators/all/${symbol}` : null,
    fetcher,
    { refreshInterval: 60000 }
  );

  return {
    indicators: data?.indicators || {},
    error,
    isLoading,
  };
};

// Hook for portfolio
export const usePortfolio = () => {
  const { data, error, isLoading, mutate } = useSWR(
    '/trading/portfolio',
    fetcher,
    { refreshInterval: 10000 }
  );

  return {
    portfolio: data?.positions || [],
    totalValue: data?.total_value ?? 0,
    cashBalance: data?.cash_balance ?? data?.balance ?? 0,
    error,
    isLoading,
    mutate,
  };
};

// Hook for watchlists
export const useWatchlists = () => {
  const { data, error, isLoading, mutate } = useSWR(
    '/trading/watchlists',
    fetcher
  );

  return {
    watchlists: data?.watchlists || [],
    error,
    isLoading,
    mutate,
  };
};

// Hook for market symbols
export const useSymbols = (market?: string) => {
  const { data, error, isLoading } = useSWR(
    `/market-data/symbols${market ? `?market=${market}` : ''}`,
    fetcher
  );

  return {
    symbols: data?.symbols || [],
    error,
    isLoading,
  };
};
