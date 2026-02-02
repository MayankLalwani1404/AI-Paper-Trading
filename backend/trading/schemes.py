from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class BuySellRequest(BaseModel):
    symbol: str
    quantity: int
    price: float


class TradeResponse(BaseModel):
    symbol: str
    quantity: int
    price: float
    side: str
    balance: float


class OrderRequest(BaseModel):
    symbol: str
    quantity: int
    price: Optional[float] = None
    side: str  # BUY / SELL
    order_type: str = "MARKET"  # MARKET / LIMIT
    exit_rules: Optional[Dict[str, Any]] = None


class OrderResponse(BaseModel):
    id: int
    symbol: str
    quantity: int
    price: Optional[float]
    side: str
    order_type: str
    status: str
    balance: float


class WatchlistCreate(BaseModel):
    name: str


class WatchlistItemCreate(BaseModel):
    symbol: str


class WatchlistResponse(BaseModel):
    id: int
    name: str
    symbols: List[str]
