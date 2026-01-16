from sqlalchemy.orm import Session
from backend.trading.models import Account, Position, Trade


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
