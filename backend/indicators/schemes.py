from pydantic import BaseModel
from typing import List


class OHLCV(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float


class IndicatorResult(BaseModel):
    name: str
    values: List[float]
