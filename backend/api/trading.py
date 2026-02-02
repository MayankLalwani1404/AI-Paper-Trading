from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.trading.schemes import (
    BuySellRequest,
    TradeResponse,
    OrderRequest,
    OrderResponse,
    WatchlistCreate,
    WatchlistItemCreate,
)
from backend.trading.service import (
    buy_stock,
    sell_stock,
    place_order,
    list_orders,
    create_watchlist,
    list_watchlists,
    add_watchlist_item,
    remove_watchlist_item,
    get_watchlist_items,
)
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


@router.post("/order", response_model=OrderResponse)
def order(request: OrderRequest, db: Session = Depends(get_db)):
    try:
        order, balance = place_order(
            db=db,
            symbol=request.symbol.upper(),
            quantity=request.quantity,
            side=request.side,
            order_type=request.order_type,
            price=request.price,
            exit_rules=request.exit_rules,
        )
        return {
            "id": order.id,
            "symbol": order.symbol,
            "quantity": order.quantity,
            "price": order.price,
            "side": order.side,
            "order_type": order.order_type,
            "status": order.status,
            "balance": balance,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders")
def orders(db: Session = Depends(get_db)):
    items = list_orders(db)
    return {
        "orders": [
            {
                "id": o.id,
                "symbol": o.symbol,
                "quantity": o.quantity,
                "price": o.price,
                "side": o.side,
                "order_type": o.order_type,
                "status": o.status,
                "exit_rules": o.exit_rules,
                "created_at": o.created_at,
            }
            for o in items
        ]
    }


@router.post("/watchlists")
def create_watchlist_endpoint(request: WatchlistCreate, db: Session = Depends(get_db)):
    watchlist = create_watchlist(db, request.name)
    return {"id": watchlist.id, "name": watchlist.name, "symbols": []}


@router.get("/watchlists")
def list_watchlists_endpoint(db: Session = Depends(get_db)):
    watchlists = list_watchlists(db)
    response = []
    for wl in watchlists:
        items = get_watchlist_items(db, wl.id)
        response.append(
            {
                "id": wl.id,
                "name": wl.name,
                "symbols": [i.symbol for i in items],
            }
        )
    return {"watchlists": response}


@router.post("/watchlists/{watchlist_id}/items")
def add_watchlist_item_endpoint(
    watchlist_id: int,
    request: WatchlistItemCreate,
    db: Session = Depends(get_db),
):
    item = add_watchlist_item(db, watchlist_id, request.symbol)
    return {"id": item.id, "symbol": item.symbol}


@router.delete("/watchlists/{watchlist_id}/items/{symbol}")
def remove_watchlist_item_endpoint(
    watchlist_id: int,
    symbol: str,
    db: Session = Depends(get_db),
):
    item = remove_watchlist_item(db, watchlist_id, symbol)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"removed": True, "symbol": symbol}
