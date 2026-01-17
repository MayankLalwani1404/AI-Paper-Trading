from typing import List
import math


def sma(prices: List[float], period: int) -> List[float]:
    """
    Simple Moving Average
    """
    if period <= 0:
        raise ValueError("Period must be positive")

    result = []
    for i in range(len(prices)):
        if i + 1 < period:
            result.append(math.nan)
        else:
            window = prices[i + 1 - period : i + 1]
            result.append(sum(window) / period)
    return result


def ema(prices: List[float], period: int) -> List[float]:
    """
    Exponential Moving Average
    """
    if period <= 0:
        raise ValueError("Period must be positive")

    result = []
    multiplier = 2 / (period + 1)

    for i, price in enumerate(prices):
        if i == 0:
            result.append(price)
        else:
            ema_value = (price - result[-1]) * multiplier + result[-1]
            result.append(ema_value)
    return result


def rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    Relative Strength Index
    """
    if period <= 0:
        raise ValueError("Period must be positive")

    gains = []
    losses = []

    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))

    rsi_values = [math.nan] * period

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        rsi_values.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi_values.append(100 - (100 / (1 + rs)))

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(100 - (100 / (1 + rs)))

    return rsi_values

def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    MACD (Moving Average Convergence Divergence)
    
    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    if len(prices) < slow:
        raise ValueError("Insufficient data for MACD calculation")

    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)

    macd_line = [f - s if not math.isnan(f) and not math.isnan(s) else math.nan
                 for f, s in zip(ema_fast, ema_slow)]

    signal_line = ema(macd_line, signal)
    histogram = [m - s if not math.isnan(m) and not math.isnan(s) else math.nan
                 for m, s in zip(macd_line, signal_line)]

    return macd_line, signal_line, histogram


def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> tuple:
    """
    Bollinger Bands
    
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    if period <= 0:
        raise ValueError("Period must be positive")

    middle_band = sma(prices, period)
    
    upper_band = []
    lower_band = []

    for i, price in enumerate(prices):
        if i < period - 1:
            upper_band.append(math.nan)
            lower_band.append(math.nan)
        else:
            window = prices[i + 1 - period : i + 1]
            mean = sum(window) / period
            variance = sum((x - mean) ** 2 for x in window) / period
            std = math.sqrt(variance)
            
            upper_band.append(mean + (std * std_dev))
            lower_band.append(mean - (std * std_dev))

    return upper_band, middle_band, lower_band


def atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
    """
    Average True Range
    
    Args:
        high: List of high prices
        low: List of low prices
        close: List of close prices
        period: ATR period
        
    Returns:
        List of ATR values
    """
    if len(high) != len(low) or len(low) != len(close):
        raise ValueError("High, low, and close lists must have same length")

    if period <= 0:
        raise ValueError("Period must be positive")

    tr_values = []
    for i in range(len(close)):
        if i == 0:
            tr = high[i] - low[i]
        else:
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )
        tr_values.append(tr)

    atr_values = [math.nan] * (period - 1)
    atr_values.append(sum(tr_values[:period]) / period)

    for i in range(period, len(tr_values)):
        atr_val = (atr_values[-1] * (period - 1) + tr_values[i]) / period
        atr_values.append(atr_val)

    return atr_values


def stochastic(high: List[float], low: List[float], close: List[float], 
               period: int = 14, smooth: int = 3) -> tuple:
    """
    Stochastic Oscillator
    
    Returns:
        Tuple of (%K line, %D line)
    """
    if period <= 0:
        raise ValueError("Period must be positive")

    k_values = []
    for i in range(len(close)):
        if i < period - 1:
            k_values.append(math.nan)
        else:
            window_high = max(high[i + 1 - period : i + 1])
            window_low = min(low[i + 1 - period : i + 1])
            
            if window_high == window_low:
                k = 50
            else:
                k = 100 * (close[i] - window_low) / (window_high - window_low)
            
            k_values.append(k)

    k_smooth = sma(k_values, smooth)
    d_smooth = sma(k_smooth, smooth)

    return k_smooth, d_smooth


def support_resistance(prices: List[float], period: int = 20) -> tuple:
    """
    Calculate support and resistance levels.
    
    Returns:
        Tuple of (support_level, resistance_level)
    """
    if len(prices) < period:
        return None, None

    recent_prices = prices[-period:]
    support = min(recent_prices)
    resistance = max(recent_prices)
    
    return support, resistance