"""
Indicator service that combines technical indicators with market data.
Handles calculation, caching, and signal generation.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.indicators import technical
from backend.market_data.service import market_data_service
from backend.market_data.cache import market_data_cache


class IndicatorService:
    """
    Service for calculating technical indicators on market data.
    """

    # Available indicators and their parameters
    AVAILABLE_INDICATORS = {
        "SMA": {"label": "Simple Moving Average", "default_period": 20},
        "EMA": {"label": "Exponential Moving Average", "default_period": 20},
        "RSI": {"label": "Relative Strength Index", "default_period": 14},
        "MACD": {"label": "MACD", "default_params": {"fast": 12, "slow": 26, "signal": 9}},
        "BOLLINGER": {"label": "Bollinger Bands", "default_period": 20},
        "ATR": {"label": "Average True Range", "default_period": 14},
        "STOCHASTIC": {"label": "Stochastic Oscillator", "default_period": 14},
        "SUPPORT_RESISTANCE": {"label": "Support & Resistance", "default_period": 20},
    }

    @classmethod
    def calculate_indicator(
        cls,
        symbol: str,
        indicator_name: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate an indicator for a symbol.
        
        Args:
            symbol: Trading symbol
            indicator_name: Name of indicator (SMA, EMA, RSI, etc.)
            **kwargs: Indicator-specific parameters
            
        Returns:
            Dictionary with indicator results or None on failure
        """
        indicator_name = indicator_name.upper()

        if indicator_name not in cls.AVAILABLE_INDICATORS:
            return None

        # Fetch market data
        ohlcv = market_data_service.fetch_ohlcv(symbol)
        if not ohlcv or len(ohlcv) == 0:
            return None

        try:
            # Extract prices
            closes = [candle["close"] for candle in ohlcv]
            highs = [candle["high"] for candle in ohlcv]
            lows = [candle["low"] for candle in ohlcv]

            result = {
                "symbol": symbol,
                "indicator": indicator_name,
                "values": [],
                "metadata": {}
            }

            if indicator_name == "SMA":
                period = kwargs.get("period", cls.AVAILABLE_INDICATORS["SMA"]["default_period"])
                values = technical.sma(closes, period)
                result["values"] = values
                result["metadata"] = {"period": period}

            elif indicator_name == "EMA":
                period = kwargs.get("period", cls.AVAILABLE_INDICATORS["EMA"]["default_period"])
                values = technical.ema(closes, period)
                result["values"] = values
                result["metadata"] = {"period": period}

            elif indicator_name == "RSI":
                period = kwargs.get("period", cls.AVAILABLE_INDICATORS["RSI"]["default_period"])
                values = technical.rsi(closes, period)
                result["values"] = values
                result["metadata"] = {"period": period, "overbought": 70, "oversold": 30}

            elif indicator_name == "MACD":
                fast = kwargs.get("fast", 12)
                slow = kwargs.get("slow", 26)
                signal = kwargs.get("signal", 9)
                macd_line, signal_line, histogram = technical.macd(closes, fast, slow, signal)
                result["values"] = {
                    "macd": macd_line,
                    "signal": signal_line,
                    "histogram": histogram
                }
                result["metadata"] = {"fast": fast, "slow": slow, "signal": signal}

            elif indicator_name == "BOLLINGER":
                period = kwargs.get("period", cls.AVAILABLE_INDICATORS["BOLLINGER"]["default_period"])
                std_dev = kwargs.get("std_dev", 2.0)
                upper, middle, lower = technical.bollinger_bands(closes, period, std_dev)
                result["values"] = {
                    "upper": upper,
                    "middle": middle,
                    "lower": lower
                }
                result["metadata"] = {"period": period, "std_dev": std_dev}

            elif indicator_name == "ATR":
                period = kwargs.get("period", cls.AVAILABLE_INDICATORS["ATR"]["default_period"])
                values = technical.atr(highs, lows, closes, period)
                result["values"] = values
                result["metadata"] = {"period": period}

            elif indicator_name == "STOCHASTIC":
                period = kwargs.get("period", cls.AVAILABLE_INDICATORS["STOCHASTIC"]["default_period"])
                smooth = kwargs.get("smooth", 3)
                k_values, d_values = technical.stochastic(highs, lows, closes, period, smooth)
                result["values"] = {
                    "k": k_values,
                    "d": d_values
                }
                result["metadata"] = {"period": period, "smooth": smooth}

            elif indicator_name == "SUPPORT_RESISTANCE":
                period = kwargs.get("period", cls.AVAILABLE_INDICATORS["SUPPORT_RESISTANCE"]["default_period"])
                support, resistance = technical.support_resistance(closes, period)
                result["values"] = {
                    "support": support,
                    "resistance": resistance
                }
                result["metadata"] = {"period": period}

            # Cache the result
            market_data_cache.set_indicator(symbol, indicator_name, result["values"])

            return result

        except Exception as e:
            print(f"Error calculating indicator {indicator_name} for {symbol}: {e}")
            return None

    @classmethod
    def get_all_indicators(cls, symbol: str) -> Dict[str, Any]:
        """
        Calculate all available indicators for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with all indicator results
        """
        results = {
            "symbol": symbol,
            "indicators": {},
            "last_price": market_data_service.get_latest_price(symbol)
        }

        for indicator_name in cls.AVAILABLE_INDICATORS.keys():
            result = cls.calculate_indicator(symbol, indicator_name)
            if result:
                results["indicators"][indicator_name] = result

        return results

    @classmethod
    def generate_signals(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate trading signals based on multiple indicators.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with signal analysis
        """
        try:
            ohlcv = market_data_service.fetch_ohlcv(symbol)
            if not ohlcv or len(ohlcv) < 50:
                return None

            closes = [candle["close"] for candle in ohlcv]
            highs = [candle["high"] for candle in ohlcv]
            lows = [candle["low"] for candle in ohlcv]
            latest_price = closes[-1]

            signals = {
                "symbol": symbol,
                "timestamp": ohlcv[-1]["date"],
                "current_price": latest_price,
                "buy_signals": [],
                "sell_signals": [],
                "neutral_indicators": [],
                "score": 0  # -100 to +100
            }

            # RSI Analysis
            rsi_values = technical.rsi(closes, 14)
            if len(rsi_values) > 0:
                latest_rsi = rsi_values[-1]
                if latest_rsi < 30:
                    signals["buy_signals"].append(f"RSI Oversold ({latest_rsi:.2f})")
                elif latest_rsi > 70:
                    signals["sell_signals"].append(f"RSI Overbought ({latest_rsi:.2f})")
                else:
                    signals["neutral_indicators"].append(f"RSI: {latest_rsi:.2f}")

            # SMA Crossover (20-period vs 50-period)
            sma20 = technical.sma(closes, 20)
            sma50 = technical.sma(closes, 50)
            if len(sma20) > 0 and len(sma50) > 0 and not any(v == float('nan') for v in [sma20[-1], sma50[-1]]):
                if sma20[-1] > sma50[-1]:
                    signals["buy_signals"].append("SMA 20 > SMA 50 (Bullish Trend)")
                    signals["score"] += 20
                else:
                    signals["sell_signals"].append("SMA 20 < SMA 50 (Bearish Trend)")
                    signals["score"] -= 20

            # Bollinger Bands
            upper, middle, lower = technical.bollinger_bands(closes, 20)
            if len(upper) > 0 and not (upper[-1] == float('nan')):
                if latest_price > upper[-1]:
                    signals["sell_signals"].append("Price Above Upper Bollinger Band")
                    signals["score"] -= 10
                elif latest_price < lower[-1]:
                    signals["buy_signals"].append("Price Below Lower Bollinger Band")
                    signals["score"] += 10
                else:
                    signals["neutral_indicators"].append(f"Within Bollinger Bands")

            # Support & Resistance
            support, resistance = technical.support_resistance(closes, 20)
            if support and resistance:
                if latest_price < support * 1.02:  # Near support
                    signals["buy_signals"].append(f"Near Support ({support:.2f})")
                    signals["score"] += 15
                elif latest_price > resistance * 0.98:  # Near resistance
                    signals["sell_signals"].append(f"Near Resistance ({resistance:.2f})")
                    signals["score"] -= 15

            # Overall signal
            if signals["score"] > 30:
                signals["recommendation"] = "STRONG BUY"
            elif signals["score"] > 10:
                signals["recommendation"] = "BUY"
            elif signals["score"] < -30:
                signals["recommendation"] = "STRONG SELL"
            elif signals["score"] < -10:
                signals["recommendation"] = "SELL"
            else:
                signals["recommendation"] = "NEUTRAL"

            # Cache the signal
            market_data_cache.set_signal(symbol, signals)

            return signals

        except Exception as e:
            print(f"Error generating signals for {symbol}: {e}")
            return None


# Singleton instance
indicator_service = IndicatorService()
