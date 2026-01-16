from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.trading.schemes import BuySellRequest, TradeResponse
from backend.trading.service import buy_stock, sell_stock
from backend.trading.models import Position, Account

router = APIRouter(prefix="/trading", tags=["trading"])

@router.post("/buy", response_model=TradeResponse)
def buy(request: BuySellRequest, db: Session = Depends(get_db)):
    try:
        trade, balance = buy_stock(
            db=db,
            symbol=request.symbol.upper(),
            quantity=request.quantity,
            price=request.price,
        )
        return {
            "symbol": trade.symbol,
            "quantity": trade.quantity,
            "price": trade.price,
            "side": trade.side,
            "balance": balance,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sell", response_model=TradeResponse)
def sell(request: BuySellRequest, db: Session = Depends(get_db)):
    try:
        trade, balance = sell_stock(
            db=db,
            symbol=request.symbol.upper(),
            quantity=request.quantity,
            price=request.price,
        )
        return {
            "symbol": trade.symbol,
            "quantity": trade.quantity,
            "price": trade.price,
            "side": trade.side,
            "balance": balance,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolio")
def portfolio(db: Session = Depends(get_db)):
    account = db.query(Account).first()
    positions = db.query(Position).all()

    return {
        "balance": account.balance if account else 0,
        "positions": [
            {
                "symbol": p.symbol,
                "quantity": p.quantity,
                "avg_price": p.avg_price,
            }
            for p in positions
        ],
    }
