"""
Market data service with Yahoo Finance integration and local dataset fallback.
Handles OHLCV data fetching, caching, and normalization across markets.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
import yfinance as yf
from backend.market_data.symbols import SYMBOL_REGISTRY, MarketType
from backend.market_data.cache import market_data_cache


class MarketDataService:
    """
    Central service for market data operations.
    - Fetches from Yahoo Finance with fallback to local datasets
    - Manages caching via Redis
    - Normalizes data across markets
    """

    # Local dataset paths (relative to project root)
    DATASET_BASE_PATH = "/home/mayank/Desktop/AI Paper Trading/datasets"

    # Mapping of dataset filenames to symbol information
    DATASET_MAPPING = {
        "AAPL_historical.csv": {
            "symbol": "AAPL",
            "market": MarketType.US,
            "columns": {"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
        },
        "ADANIPORTS.csv": {
            "symbol": "ADANIPORTS.NS",
            "market": MarketType.NSE,
            "columns": {"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
        },
        "ohlc.csv": {
            "symbol": "VARIOUS",  # Multi-symbol dataset
            "market": MarketType.US,
            "columns": {"Date": "date", "symbol": "symbol", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
        },
        "historical_stock_prices.csv": {
            "symbol": "VARIOUS",  # Multi-symbol dataset
            "market": MarketType.US,
            "columns": {"date": "date", "symbol": "symbol", "open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"}
        },
        "BTCUSDT_5m_2017-09-01_to_2025-09-23.csv": {
            "symbol": "BTCUSDT",
            "market": MarketType.CRYPTO,
            "columns": {"date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
        }
    }

    @classmethod
    def fetch_ohlcv(
        cls,
        symbol: str,
        interval: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch OHLCV data for a symbol.
        Tries cache first, then Yahoo Finance, then local datasets.
        
        Args:
            symbol: Trading symbol (will be normalized)
            interval: Candle interval (1m, 5m, 1h, 1d, 1w, etc.)
            start_date: Start date as YYYY-MM-DD
            end_date: End date as YYYY-MM-DD
            use_cache: Whether to check cache first
            
        Returns:
            List of OHLCV dictionaries or None on failure
        """
        symbol = symbol.upper().strip()
        
        # Try cache first
        if use_cache:
            cached = market_data_cache.get_ohlcv(symbol, interval)
            if cached:
                return cached

        # Try Yahoo Finance
        ohlcv = cls._fetch_from_yahoo_finance(symbol, interval, start_date, end_date)
        if ohlcv:
            # Cache the result
            market_data_cache.set_ohlcv(symbol, interval, ohlcv)
            return ohlcv

        # Fallback to local datasets
        ohlcv = cls._fetch_from_local_dataset(symbol, start_date, end_date)
        if ohlcv:
            market_data_cache.set_ohlcv(symbol, interval, ohlcv)
            return ohlcv

        return None

    @staticmethod
    def _fetch_from_yahoo_finance(
        symbol: str,
        interval: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch data from Yahoo Finance.
        
        Args:
            symbol: Trading symbol
            interval: Candle interval
            start_date: Start date as YYYY-MM-DD
            end_date: End date as YYYY-MM-DD
            
        Returns:
            List of OHLCV dictionaries or None on failure
        """
        try:
            # Set default dates
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                # Default to 1 year of data
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            # Fetch data
            ticker = yf.Ticker(symbol)
            df = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False
            )

            if df.empty:
                return None

            # Normalize columns - handle multi-index from yfinance
            df = df.reset_index()
            # Flatten column names if multi-index (tuple)
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            df.columns = [col.lower() for col in df.columns]

            # Ensure required columns exist
            required_cols = {"date", "open", "high", "low", "close", "volume"}
            if not required_cols.issubset(set(df.columns)):
                return None

            # Convert to list of dictionaries
            ohlcv_list = []
            for _, row in df.iterrows():
                ohlcv_list.append({
                    "date": row["date"].isoformat() if hasattr(row["date"], "isoformat") else str(row["date"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"])
                })

            return ohlcv_list

        except Exception as e:
            print(f"Error fetching from Yahoo Finance for {symbol}: {e}")
            return None

    @classmethod
    def _fetch_from_local_dataset(
        cls,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch data from local CSV datasets.
        
        Args:
            symbol: Trading symbol
            start_date: Start date as YYYY-MM-DD
            end_date: End date as YYYY-MM-DD
            
        Returns:
            List of OHLCV dictionaries or None on failure
        """
        try:
            symbol = symbol.upper().strip()

            # Search for matching dataset
            for filename, config in cls.DATASET_MAPPING.items():
                file_path = os.path.join(cls.DATASET_BASE_PATH, filename)

                if not os.path.exists(file_path):
                    continue

                # Check if this dataset contains the symbol
                if config["symbol"] != "VARIOUS" and config["symbol"] != symbol:
                    continue

                # Load CSV
                df = pd.read_csv(file_path)

                # Rename columns
                df = df.rename(columns=config["columns"])

                # Filter by symbol if multi-symbol dataset
                if config["symbol"] == "VARIOUS" and "symbol" in df.columns:
                    df = df[df["symbol"].str.upper() == symbol]

                if df.empty:
                    continue

                # Convert date column to datetime
                df["date"] = pd.to_datetime(df["date"])

                # Filter by date range
                if start_date:
                    start_dt = pd.to_datetime(start_date)
                    df = df[df["date"] >= start_dt]

                if end_date:
                    end_dt = pd.to_datetime(end_date)
                    df = df[df["date"] <= end_dt]

                if df.empty:
                    continue

                # Sort by date
                df = df.sort_values("date")

                # Convert to list of dictionaries
                ohlcv_list = []
                for _, row in df.iterrows():
                    date_val = row.get("date") if isinstance(row, pd.Series) else row["date"]
                    ohlcv_list.append({
                        "date": date_val.isoformat() if hasattr(date_val, "isoformat") else str(date_val),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": float(row["volume"])
                    })

                return ohlcv_list if ohlcv_list else None

            return None

        except Exception as e:
            print(f"Error fetching from local dataset for {symbol}: {e}")
            return None

    @classmethod
    def get_latest_price(cls, symbol: str) -> Optional[float]:
        """
        Get the latest available price for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest price as float or None
        """
        # Check cache first
        cached_price = market_data_cache.get_latest_price(symbol)
        if cached_price:
            return cached_price

        # Try to fetch latest data
        ohlcv = cls.fetch_ohlcv(symbol, interval="1d", use_cache=False)
        if ohlcv and len(ohlcv) > 0:
            latest_price = ohlcv[-1]["close"]
            market_data_cache.set_latest_price(symbol, latest_price)
            return latest_price

        return None

    @classmethod
    def get_multiple_prices(cls, symbols: List[str]) -> Dict[str, Optional[float]]:
        """
        Get latest prices for multiple symbols.
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary mapping symbols to prices
        """
        result = {}
        for symbol in symbols:
            result[symbol] = cls.get_latest_price(symbol)
        return result

    @classmethod
    def search_symbols(cls, query: str) -> List[str]:
        """
        Search for symbols matching a query.
        
        Args:
            query: Search query (name or symbol)
            
        Returns:
            List of matching symbols
        """
        query_lower = query.lower()
        matches = []

        for symbol, metadata in SYMBOL_REGISTRY.SYMBOL_METADATA.items():
            if (query_lower in symbol.lower() or
                query_lower in metadata.name.lower()):
                matches.append(symbol)

        return matches

    @classmethod
    def get_available_symbols(cls, market: Optional[MarketType] = None) -> List[str]:
        """
        Get list of available symbols.
        
        Args:
            market: Optional market filter
            
        Returns:
            List of available symbols
        """
        if market:
            return list(SYMBOL_REGISTRY.get_all_symbols(market))
        return list(SYMBOL_REGISTRY.get_all_symbols())

    @classmethod
    def validate_symbol(cls, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a symbol is supported.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        symbol = symbol.upper().strip()

        if not symbol:
            return False, "Symbol cannot be empty"

        if len(symbol) < 1 or len(symbol) > 10:
            return False, "Symbol length must be between 1 and 10 characters"

        # Check if symbol is registered
        if symbol in SYMBOL_REGISTRY.get_all_symbols():
            return True, None

        # Try to infer market and check
        market = SYMBOL_REGISTRY.get_market(symbol)
        return True, None  # Allow unknown symbols (will try Yahoo Finance)


# Singleton instance
market_data_service = MarketDataService()
