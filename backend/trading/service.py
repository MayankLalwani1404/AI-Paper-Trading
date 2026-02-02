from sqlalchemy.orm import Session
from backend.trading.models import Account, Position, Trade, Order, Watchlist, WatchlistItem


def get_or_create_account(db: Session) -> Account:
    account = db.query(Account).first()
    if not account:
        account = Account(balance=1_000_000.0)
        db.add(account)
        db.commit()
        db.refresh(account)
    return account


def buy_stock(db: Session, symbol: str, quantity: int, price: float):
    account = get_or_create_account(db)
    cost = quantity * price

    if account.balance < cost:
        raise ValueError("Insufficient balance")

    account.balance -= cost

    position = (
        db.query(Position)
        .filter(Position.symbol == symbol)
        .first()
    )

    if position:
        total_qty = position.quantity + quantity
        position.avg_price = (
            (position.avg_price * position.quantity) + cost
        ) / total_qty
        position.quantity = total_qty
    else:
        position = Position(
            symbol=symbol,
            quantity=quantity,
            avg_price=price,
            account_id=account.id
        )
        db.add(position)

    trade = Trade(
        symbol=symbol,
        quantity=quantity,
        price=price,
        side="BUY",
        account_id=account.id
    )

    db.add(trade)
    db.commit()

    return trade, account.balance


def sell_stock(db: Session, symbol: str, quantity: int, price: float):
    account = get_or_create_account(db)

    position = (
        db.query(Position)
        .filter(Position.symbol == symbol)
        .first()
    )

    if not position or position.quantity < quantity:
        raise ValueError("Insufficient shares")

    position.quantity -= quantity
    proceeds = quantity * price
    account.balance += proceeds

    if position.quantity == 0:
        db.delete(position)

    trade = Trade(
        symbol=symbol,
        quantity=quantity,
        price=price,
        side="SELL",
        account_id=account.id
    )

    db.add(trade)
    db.commit()

    return trade, account.balance


def place_order(
    db: Session,
    symbol: str,
    quantity: int,
    side: str,
    order_type: str = "MARKET",
    price: float = None,
    exit_rules: dict = None,
):
    account = get_or_create_account(db)
    side = side.upper()
    order_type = order_type.upper()

    if side not in {"BUY", "SELL"}:
        raise ValueError("Invalid side. Use BUY or SELL")

    if order_type not in {"MARKET", "LIMIT"}:
        raise ValueError("Invalid order type. Use MARKET or LIMIT")

    if order_type == "LIMIT" and price is None:
        raise ValueError("Limit orders require price")

    # For paper trading, execute immediately at price (or last price if market)
    if price is None:
        raise ValueError("Price is required for now (paper execution)")

    if side == "BUY":
        trade, balance = buy_stock(db, symbol, quantity, price)
    else:
        trade, balance = sell_stock(db, symbol, quantity, price)

    order = Order(
        symbol=trade.symbol,
        quantity=trade.quantity,
        price=trade.price,
        side=trade.side,
        order_type=order_type,
        status="FILLED",
        exit_rules=exit_rules,
        account_id=trade.account_id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return order, balance


def list_orders(db: Session):
    return db.query(Order).order_by(Order.created_at.desc()).all()


def create_watchlist(db: Session, name: str):
    account = get_or_create_account(db)
    watchlist = Watchlist(name=name, account_id=account.id)
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    return watchlist


def list_watchlists(db: Session):
    account = get_or_create_account(db)
    return db.query(Watchlist).filter(Watchlist.account_id == account.id).all()


def add_watchlist_item(db: Session, watchlist_id: int, symbol: str):
    item = WatchlistItem(watchlist_id=watchlist_id, symbol=symbol.upper())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_watchlist_item(db: Session, watchlist_id: int, symbol: str):
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.watchlist_id == watchlist_id)
        .filter(WatchlistItem.symbol == symbol.upper())
        .first()
    )
    if item:
        db.delete(item)
        db.commit()
    return item


def get_watchlist_items(db: Session, watchlist_id: int):
    return (
        db.query(WatchlistItem)
        .filter(WatchlistItem.watchlist_id == watchlist_id)
        .all()
    )
