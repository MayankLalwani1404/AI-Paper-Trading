"""
API endpoints for market data and OHLCV information.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.market_data.service import market_data_service
from backend.market_data.symbols import SYMBOL_REGISTRY, MarketType
from backend.indicators.schemes import OHLCV

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/ohlcv")
async def get_ohlcv(
    symbol: str,
    interval: str = Query("1d", description="Candle interval: 1m, 5m, 15m, 1h, 1d, 1w"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
):
    """
    Get OHLCV data for a symbol.
    
    - Fetches from Yahoo Finance or local datasets
    - Caches results in Redis
    - Supports multiple time intervals
    """
    try:
        ohlcv = market_data_service.fetch_ohlcv(
            symbol=symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )

        if not ohlcv:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {symbol}"
            )

        return {
            "symbol": symbol,
            "interval": interval,
            "data": ohlcv,
            "count": len(ohlcv)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest-price")
async def get_latest_price(symbol: str):
    """
    Get the latest available price for a symbol.
    """
    try:
        price = market_data_service.get_latest_price(symbol)

        if price is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch price for {symbol}"
            )

        return {
            "symbol": symbol,
            "price": price
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prices")
async def get_multiple_prices(symbols: List[str]):
    """
    Get latest prices for multiple symbols.
    """
    try:
        prices = market_data_service.get_multiple_prices(symbols)
        return {
            "prices": prices
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_symbols(query: str):
    """
    Search for symbols by name or ticker.
    """
    try:
        results = market_data_service.search_symbols(query)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbols")
async def get_symbols(market: Optional[str] = Query(None, description="Market: US, NSE, BSE, CRYPTO, INDEX")):
    """
    Get list of available symbols.
    """
    try:
        market_type = None
        if market:
            try:
                market_type = MarketType(market.upper())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid market: {market}. Must be one of: {', '.join([m.value for m in MarketType])}"
                )

        symbols = market_data_service.get_available_symbols(market_type)

        return {
            "market": market,
            "symbols": symbols,
            "count": len(symbols)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbols/by-market")
async def get_symbols_by_market():
    """
    Get all symbols grouped by market.
    """
    try:
        symbols_by_market = SYMBOL_REGISTRY.get_symbols_by_market()
        return {
            "markets": {
                market.value: list(symbols)
                for market, symbols in symbols_by_market.items()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-symbol")
async def validate_symbol(symbol: str):
    """
    Validate if a symbol is supported.
    """
    try:
        is_valid, error_message = market_data_service.validate_symbol(symbol)

        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        return {
            "symbol": symbol.upper(),
            "valid": is_valid
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{symbol}")
async def get_symbol_info(symbol: str):
    """
    Get metadata information for a symbol.
    """
    try:
        metadata = SYMBOL_REGISTRY.get_metadata(symbol)

        if not metadata:
            # Try to infer market
            market = SYMBOL_REGISTRY.get_market(symbol)
            return {
                "symbol": symbol.upper(),
                "market": market.value if market else "UNKNOWN",
                "registered": False
            }

        return {
            "symbol": metadata.symbol,
            "market": metadata.market.value,
            "name": metadata.name,
            "sector": metadata.sector,
            "country": metadata.country,
            "registered": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
