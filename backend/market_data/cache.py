"""
Redis caching layer for market data with TTL management.
Handles efficient storage and retrieval of OHLCV data and indicators.
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from backend.core.redis import redis_client


class MarketDataCache:
    """
    Manages Redis cache for market data with TTL policies.
    """

    # TTL policies (in seconds)
    TTL_INTRADAY_5M = 300  # 5 minutes for 5m candles
    TTL_INTRADAY_15M = 900  # 15 minutes for 15m candles
    TTL_INTRADAY_1H = 3600  # 1 hour for 1h candles
    TTL_DAILY = 86400  # 24 hours for daily candles
    TTL_WEEKLY = 604800  # 7 days for weekly candles
    TTL_INDICATOR = 14400  # 4 hours for indicators
    TTL_SIGNAL = 1800  # 30 minutes for trade signals
    TTL_LATEST_PRICE = 60  # 1 minute for latest prices

    @staticmethod
    def _get_ttl_for_interval(interval: str) -> int:
        """
        Get appropriate TTL based on candle interval.
        
        Args:
            interval: Candle interval (e.g., '1m', '5m', '1h', '1d', '1w')
            
        Returns:
            TTL in seconds
        """
        interval_ttls = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
            "1w": 604800,
            "1mo": 2592000,  # 30 days
        }
        return interval_ttls.get(interval, 3600)  # Default to 1 hour

    @staticmethod
    def build_ohlcv_key(symbol: str, interval: str, date: Optional[str] = None) -> str:
        """Build cache key for OHLCV data"""
        if date:
            return f"ohlcv:{symbol}:{interval}:{date}"
        return f"ohlcv:{symbol}:{interval}:latest"

    @staticmethod
    def build_indicator_key(symbol: str, indicator_name: str, date: Optional[str] = None) -> str:
        """Build cache key for indicator data"""
        if date:
            return f"indicator:{symbol}:{indicator_name}:{date}"
        return f"indicator:{symbol}:{indicator_name}:latest"

    @staticmethod
    def build_signal_key(symbol: str) -> str:
        """Build cache key for trade signals"""
        return f"signal:{symbol}"

    @staticmethod
    def build_price_key(symbol: str) -> str:
        """Build cache key for latest price"""
        return f"price:{symbol}:latest"

    @staticmethod
    def build_portfolio_key(account_id: int) -> str:
        """Build cache key for portfolio data"""
        return f"portfolio:{account_id}"

    @classmethod
    def set_ohlcv(
        cls,
        symbol: str,
        interval: str,
        ohlcv_list: List[Dict[str, Any]],
        date: Optional[str] = None
    ) -> bool:
        """
        Cache OHLCV data with interval-appropriate TTL.
        
        Args:
            symbol: Trading symbol
            interval: Candle interval
            ohlcv_list: List of OHLCV dictionaries
            date: Optional date for partitioning
            
        Returns:
            Success status
        """
        key = cls.build_ohlcv_key(symbol, interval, date)
        ttl = cls._get_ttl_for_interval(interval)
        
        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(ohlcv_list)
            )
            return True
        except Exception as e:
            print(f"Error caching OHLCV for {symbol}: {e}")
            return False

    @classmethod
    def get_ohlcv(
        cls,
        symbol: str,
        interval: str,
        date: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached OHLCV data.
        
        Args:
            symbol: Trading symbol
            interval: Candle interval
            date: Optional date for partitioning
            
        Returns:
            List of OHLCV dictionaries or None if not found/expired
        """
        key = cls.build_ohlcv_key(symbol, interval, date)
        
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Error retrieving OHLCV from cache: {e}")
        
        return None

    @classmethod
    def set_indicator(
        cls,
        symbol: str,
        indicator_name: str,
        values: List[float],
        date: Optional[str] = None
    ) -> bool:
        """
        Cache indicator calculation results.
        
        Args:
            symbol: Trading symbol
            indicator_name: Name of indicator (RSI, EMA, etc.)
            values: List of indicator values
            date: Optional date for partitioning
            
        Returns:
            Success status
        """
        key = cls.build_indicator_key(symbol, indicator_name, date)
        
        try:
            redis_client.setex(
                key,
                cls.TTL_INDICATOR,
                json.dumps(values)
            )
            return True
        except Exception as e:
            print(f"Error caching indicator: {e}")
            return False

    @classmethod
    def get_indicator(
        cls,
        symbol: str,
        indicator_name: str,
        date: Optional[str] = None
    ) -> Optional[List[float]]:
        """
        Retrieve cached indicator values.
        
        Args:
            symbol: Trading symbol
            indicator_name: Name of indicator
            date: Optional date for partitioning
            
        Returns:
            List of indicator values or None if not found/expired
        """
        key = cls.build_indicator_key(symbol, indicator_name, date)
        
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Error retrieving indicator from cache: {e}")
        
        return None

    @classmethod
    def set_signal(
        cls,
        symbol: str,
        signal_data: Dict[str, Any]
    ) -> bool:
        """
        Cache trade signal data.
        
        Args:
            symbol: Trading symbol
            signal_data: Signal dictionary with metadata
            
        Returns:
            Success status
        """
        key = cls.build_signal_key(symbol)
        
        try:
            redis_client.setex(
                key,
                cls.TTL_SIGNAL,
                json.dumps(signal_data)
            )
            return True
        except Exception as e:
            print(f"Error caching signal: {e}")
            return False

    @classmethod
    def get_signal(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached trade signal.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Signal dictionary or None if not found/expired
        """
        key = cls.build_signal_key(symbol)
        
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Error retrieving signal from cache: {e}")
        
        return None

    @classmethod
    def set_latest_price(cls, symbol: str, price: float) -> bool:
        """
        Cache latest price for a symbol.
        
        Args:
            symbol: Trading symbol
            price: Latest price
            
        Returns:
            Success status
        """
        key = cls.build_price_key(symbol)
        
        try:
            redis_client.setex(
                key,
                cls.TTL_LATEST_PRICE,
                str(price)
            )
            return True
        except Exception as e:
            print(f"Error caching price: {e}")
            return False

    @classmethod
    def get_latest_price(cls, symbol: str) -> Optional[float]:
        """
        Retrieve cached latest price.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Price as float or None if not found/expired
        """
        key = cls.build_price_key(symbol)
        
        try:
            data = redis_client.get(key)
            if data:
                return float(data)
        except Exception as e:
            print(f"Error retrieving price from cache: {e}")
        
        return None

    @classmethod
    def set_portfolio_cache(
        cls,
        account_id: int,
        portfolio_data: Dict[str, Any],
        ttl: int = 300  # 5 minutes default
    ) -> bool:
        """
        Cache portfolio data.
        
        Args:
            account_id: Account ID
            portfolio_data: Portfolio dictionary
            ttl: TTL in seconds
            
        Returns:
            Success status
        """
        key = cls.build_portfolio_key(account_id)
        
        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(portfolio_data)
            )
            return True
        except Exception as e:
            print(f"Error caching portfolio: {e}")
            return False

    @classmethod
    def get_portfolio_cache(cls, account_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached portfolio data.
        
        Args:
            account_id: Account ID
            
        Returns:
            Portfolio dictionary or None if not found/expired
        """
        key = cls.build_portfolio_key(account_id)
        
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Error retrieving portfolio from cache: {e}")
        
        return None

    @classmethod
    def invalidate_symbol_cache(cls, symbol: str) -> bool:
        """
        Invalidate all cache entries for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Success status
        """
        try:
            # Find and delete all keys matching pattern
            pattern = f"*:{symbol}:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error invalidating cache for {symbol}: {e}")
            return False

    @classmethod
    def clear_all_cache(cls) -> bool:
        """Clear all market data cache"""
        try:
            redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False


# Singleton instance
market_data_cache = MarketDataCache()
