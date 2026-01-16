from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, nullable=False, default=1_000_000.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    side = Column(String, nullable=False)  # BUY / SELL
    account_id = Column(Integer, ForeignKey("accounts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
