from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from backend.ai.filter import parse_query, apply_filter
from backend.ai.patterns import detect_patterns
from backend.market_data.service import market_data_service
from backend.market_data.symbols import MarketType

router = APIRouter(prefix="/ai", tags=["ai"])


class AIQueryRequest(BaseModel):
    query: str
    market: Optional[str] = None
    limit: int = 25


class PatternRequest(BaseModel):
    symbol: str
    holding_period: Optional[str] = None  # e.g., "1 day", "1 week", "1 month"


def _map_holding_to_interval(holding_period: Optional[str]) -> str:
    if not holding_period:
        return "1d"
    hp = holding_period.lower().strip()
    if "hour" in hp:
        return "1h"
    if "day" in hp:
        return "1d"
    if "week" in hp:
        return "1w"
    if "month" in hp:
        return "1mo"
    if "year" in hp:
        return "1mo"
    return "1d"


@router.post("/filter")
def ai_filter(request: AIQueryRequest):
    try:
        spec = parse_query(request.query)

        market = request.market
        market_type = None
        if market:
            try:
                market_type = MarketType(market.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid market")

        symbols = market_data_service.get_available_symbols(market_type)
        matches = []

        for symbol in symbols[: max(10, request.limit * 2)]:
            ohlcv = market_data_service.fetch_ohlcv(symbol, interval="1d")
            if not ohlcv:
                continue
            if apply_filter(ohlcv, spec):
                matches.append(symbol)
            if len(matches) >= request.limit:
                break

        return {
            "query": request.query,
            "spec": spec,
            "results": matches,
            "count": len(matches),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patterns")
def patterns(request: PatternRequest):
    try:
        interval = _map_holding_to_interval(request.holding_period)
        ohlcv = market_data_service.fetch_ohlcv(request.symbol, interval=interval)
        if not ohlcv:
            raise HTTPException(status_code=404, detail="No data for symbol")
        patterns_found = detect_patterns(ohlcv)
        return {
            "symbol": request.symbol.upper(),
            "interval": interval,
            "patterns": patterns_found,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
