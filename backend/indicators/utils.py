from typing import List


def extract_closes(data: List[dict]) -> List[float]:
    """
    Extract closing prices from OHLCV data.
    """
    return [candle["close"] for candle in data]
