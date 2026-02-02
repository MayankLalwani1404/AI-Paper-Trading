from typing import List, Dict


def _last_n(ohlcv: List[Dict], n: int) -> List[Dict]:
    return ohlcv[-n:] if len(ohlcv) >= n else ohlcv


def detect_bullish_engulfing(ohlcv: List[Dict]) -> bool:
    candles = _last_n(ohlcv, 2)
    if len(candles) < 2:
        return False
    prev, curr = candles[0], candles[1]
    return (
        curr["close"] > curr["open"]
        and prev["close"] < prev["open"]
        and curr["close"] >= prev["open"]
        and curr["open"] <= prev["close"]
    )


def detect_double_bottom(ohlcv: List[Dict], tolerance: float = 0.02) -> bool:
    # Naive: two recent lows within tolerance and a bounce between them
    if len(ohlcv) < 20:
        return False
    closes = [c["close"] for c in ohlcv]
    lows = sorted([(v, i) for i, v in enumerate(closes)])[:5]
    lows = sorted(lows, key=lambda x: x[1])
    if len(lows) < 2:
        return False
    (low1, i1), (low2, i2) = lows[0], lows[1]
    if i2 - i1 < 3:
        return False
    if abs(low1 - low2) / max(low1, low2) > tolerance:
        return False
    mid_high = max(closes[i1:i2])
    return mid_high > max(low1, low2) * (1 + tolerance)


def detect_breakout(ohlcv: List[Dict], lookback: int = 20) -> bool:
    if len(ohlcv) < lookback + 1:
        return False
    recent = ohlcv[-(lookback + 1):]
    prev_high = max(c["high"] for c in recent[:-1])
    last = recent[-1]
    return last["close"] > prev_high


def detect_sideways_breakout(ohlcv: List[Dict], lookback: int = 15) -> bool:
    if len(ohlcv) < lookback + 5:
        return False
    recent = ohlcv[-(lookback + 5):]
    base = recent[:-5]
    highs = [c["high"] for c in base]
    lows = [c["low"] for c in base]
    if not highs or not lows:
        return False
    range_pct = (max(highs) - min(lows)) / max(1e-9, min(lows))
    # Sideways if range within 3%
    if range_pct > 0.03:
        return False
    # Breakout if last close above base high
    last = recent[-1]
    return last["close"] > max(highs)


def detect_patterns(ohlcv: List[Dict]) -> Dict[str, bool]:
    return {
        "bullish_engulfing": detect_bullish_engulfing(ohlcv),
        "double_bottom": detect_double_bottom(ohlcv),
        "breakout": detect_breakout(ohlcv),
        "sideways_breakout": detect_sideways_breakout(ohlcv),
    }
