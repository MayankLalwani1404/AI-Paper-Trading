from pydantic import BaseModel


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
