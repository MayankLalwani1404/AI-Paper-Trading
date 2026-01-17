"""
API endpoints for technical indicators and signal analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.indicators.service import indicator_service

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/available")
async def get_available_indicators():
    """
    Get list of all available indicators.
    """
    try:
        indicators_list = []
        for indicator_name, config in indicator_service.AVAILABLE_INDICATORS.items():
            indicators_list.append({
                "name": indicator_name,
                "label": config["label"],
                "default_params": config.get("default_period") or config.get("default_params")
            })

        return {
            "indicators": indicators_list,
            "count": len(indicators_list)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate")
async def calculate_indicator(
    symbol: str,
    indicator: str,
    period: Optional[int] = Query(None),
    fast: Optional[int] = Query(None),
    slow: Optional[int] = Query(None),
    signal_period: Optional[int] = Query(None),
    std_dev: Optional[float] = Query(None),
    smooth: Optional[int] = Query(None),
):
    """
    Calculate a specific indicator for a symbol.
    
    Query parameters depend on the indicator:
    - SMA/EMA/RSI/ATR/BOLLINGER/SUPPORT_RESISTANCE: period
    - MACD: fast, slow, signal_period
    - STOCHASTIC: period, smooth
    - BOLLINGER: period, std_dev
    """
    try:
        kwargs = {}
        if period is not None:
            kwargs["period"] = period
        if fast is not None:
            kwargs["fast"] = fast
        if slow is not None:
            kwargs["slow"] = slow
        if signal_period is not None:
            kwargs["signal"] = signal_period
        if std_dev is not None:
            kwargs["std_dev"] = std_dev
        if smooth is not None:
            kwargs["smooth"] = smooth

        result = indicator_service.calculate_indicator(symbol, indicator, **kwargs)

        if result is None:
            raise HTTPException(
                status_code=400,
                detail=f"Could not calculate {indicator} for {symbol}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all/{symbol}")
async def get_all_indicators(symbol: str):
    """
    Calculate all available indicators for a symbol.
    """
    try:
        result = indicator_service.get_all_indicators(symbol)

        if not result["indicators"]:
            raise HTTPException(
                status_code=400,
                detail=f"Could not fetch data for {symbol}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{symbol}")
async def get_trade_signals(symbol: str):
    """
    Generate trading signals for a symbol based on multiple indicators.
    
    Returns:
    - Buy signals: Indicators suggesting upward movement
    - Sell signals: Indicators suggesting downward movement
    - Recommendation: STRONG BUY, BUY, NEUTRAL, SELL, STRONG SELL
    - Score: -100 to +100 (negative = bearish, positive = bullish)
    """
    try:
        signals = indicator_service.generate_signals(symbol)

        if signals is None:
            raise HTTPException(
                status_code=400,
                detail=f"Could not generate signals for {symbol}"
            )

        return signals

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sma")
async def calculate_sma(symbol: str, period: int = Query(20)):
    """Calculate Simple Moving Average"""
    return await calculate_indicator(symbol, "SMA", period=period)


@router.post("/ema")
async def calculate_ema(symbol: str, period: int = Query(20)):
    """Calculate Exponential Moving Average"""
    return await calculate_indicator(symbol, "EMA", period=period)


@router.post("/rsi")
async def calculate_rsi(symbol: str, period: int = Query(14)):
    """Calculate Relative Strength Index"""
    return await calculate_indicator(symbol, "RSI", period=period)


@router.post("/macd")
async def calculate_macd(
    symbol: str,
    fast: int = Query(12),
    slow: int = Query(26),
    signal_period: int = Query(9)
):
    """Calculate MACD"""
    return await calculate_indicator(
        symbol, "MACD",
        fast=fast,
        slow=slow,
        signal_period=signal_period
    )


@router.post("/bollinger")
async def calculate_bollinger(
    symbol: str,
    period: int = Query(20),
    std_dev: float = Query(2.0)
):
    """Calculate Bollinger Bands"""
    return await calculate_indicator(symbol, "BOLLINGER", period=period, std_dev=std_dev)


@router.post("/atr")
async def calculate_atr(symbol: str, period: int = Query(14)):
    """Calculate Average True Range"""
    return await calculate_indicator(symbol, "ATR", period=period)


@router.post("/stochastic")
async def calculate_stochastic(
    symbol: str,
    period: int = Query(14),
    smooth: int = Query(3)
):
    """Calculate Stochastic Oscillator"""
    return await calculate_indicator(symbol, "STOCHASTIC", period=period, smooth=smooth)
