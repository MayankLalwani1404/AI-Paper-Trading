import re
from typing import Dict, Any, List, Optional
import requests

from backend.core.config import settings
from backend.indicators import technical
from backend.ai.patterns import detect_patterns


def _extract_int(pattern: str, text: str) -> Optional[int]:
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def parse_query_rules(query: str) -> Dict[str, Any]:
    q = query.lower()
    spec: Dict[str, Any] = {"raw": query}

    # Market hints
    if "indian" in q or "nse" in q or "bse" in q:
        spec["market"] = "INDIA"
    if "us" in q or "nasdaq" in q or "nyse" in q:
        spec["market"] = "US"

    # RSI
    rsi_above = _extract_int(r"rsi\s*(?:above|over|crossed above)\s*(\d+)", q)
    rsi_below = _extract_int(r"rsi\s*(?:below|under)\s*(\d+)", q)
    if rsi_above is not None:
        spec["rsi_above"] = rsi_above
    if rsi_below is not None:
        spec["rsi_below"] = rsi_below

    # Moving averages
    ma_above = _extract_int(r"above their (\d+)-day moving average", q)
    ma_below = _extract_int(r"below their (\d+)-day moving average", q)
    if ma_above is not None:
        spec["ma_above"] = ma_above
    if ma_below is not None:
        spec["ma_below"] = ma_below

    # MACD crossover
    if "macd" in q and "bullish" in q:
        spec["macd_cross"] = "bullish"

    # Volume trend
    if "rising volume" in q or "increasing volume" in q:
        spec["volume_trend"] = "rising"

    # Price drop
    drop_pct = _extract_int(r"dropped more than (\d+)%", q)
    if drop_pct is not None:
        spec["price_drop_pct"] = drop_pct

    # Patterns
    if "double bottom" in q:
        spec["pattern"] = "double_bottom"
    if "bullish engulfing" in q:
        spec["pattern"] = "bullish_engulfing"
    if "broke above their resistance" in q or "broke above resistance" in q:
        spec["pattern"] = "breakout"
    if "sideways" in q and "moving up" in q:
        spec["pattern"] = "sideways_breakout"

    # Time window
    days = _extract_int(r"last (\d+) days", q)
    if days is not None:
        spec["days"] = days
    weeks = _extract_int(r"last (\d+) weeks", q)
    if weeks is not None:
        spec["days"] = weeks * 5

    return spec


def parse_query_with_llm(query: str) -> Optional[Dict[str, Any]]:
    if not settings.OLLAMA_BASE_URL:
        return None

    prompt = (
        "You are a financial query parser. Convert the user query to JSON. "
        "Return only JSON with keys: market, rsi_above, rsi_below, ma_above, ma_below, "
        "macd_cross, volume_trend, price_drop_pct, pattern, days, limit. "
        "If a field is not present, omit it.\n\n"
        f"Query: {query}"
    )

    try:
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=20,
        )
        response.raise_for_status()
        text = response.json().get("response", "{}").strip()
        return _safe_json(text)
    except Exception:
        return None


def _safe_json(text: str) -> Optional[Dict[str, Any]]:
    try:
        import json
        return json.loads(text)
    except Exception:
        return None


def _volume_rising(volumes: List[float]) -> bool:
    if len(volumes) < 6:
        return False
    recent = sum(volumes[-3:]) / 3
    prior = sum(volumes[-6:-3]) / 3
    return recent > prior


def apply_filter(ohlcv: List[Dict], spec: Dict[str, Any]) -> bool:
    closes = [c["close"] for c in ohlcv]
    highs = [c["high"] for c in ohlcv]
    lows = [c["low"] for c in ohlcv]
    volumes = [c["volume"] for c in ohlcv]

    # RSI
    if "rsi_above" in spec or "rsi_below" in spec:
        rsi_val = technical.rsi(closes, period=14)[-1]
        if rsi_val is None:
            return False
        if "rsi_above" in spec and rsi_val < spec["rsi_above"]:
            return False
        if "rsi_below" in spec and rsi_val > spec["rsi_below"]:
            return False

    # Moving averages
    if "ma_above" in spec:
        ma = technical.sma(closes, period=int(spec["ma_above"]))[-1]
        if ma is None or closes[-1] <= ma:
            return False
    if "ma_below" in spec:
        ma = technical.sma(closes, period=int(spec["ma_below"]))[-1]
        if ma is None or closes[-1] >= ma:
            return False

    # MACD
    if spec.get("macd_cross") == "bullish":
        macd_line, signal_line, _ = technical.macd(closes)
        if not macd_line or not signal_line:
            return False
        if macd_line[-1] <= signal_line[-1]:
            return False

    # Volume trend
    if spec.get("volume_trend") == "rising":
        if not _volume_rising(volumes):
            return False

    # Price drop
    if "price_drop_pct" in spec:
        if len(closes) < 2:
            return False
        change_pct = (closes[-1] - closes[-2]) / closes[-2] * 100
        if change_pct > -abs(spec["price_drop_pct"]):
            return False

    # Patterns
    if "pattern" in spec:
        patterns = detect_patterns(ohlcv)
        if not patterns.get(spec["pattern"], False):
            return False

    return True


def parse_query(query: str) -> Dict[str, Any]:
    parsed = parse_query_rules(query)
    if parsed:
        return parsed
    llm = parse_query_with_llm(query)
    return llm or {"raw": query}
