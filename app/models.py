from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enum import CurrencyEnum


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(unique=True)

class Wallet(Base):
    __tablename__ = 'wallet'
    #Уникальный идентификатор кошелька т.е. первичный ключ
    id: Mapped[int] = mapped_column(primary_key=True)
    # Название кошелька
    name: Mapped[str]
    # Баланс кошелька. Используется Decimal для точных вычислений
    balance: Mapped[Decimal]
    # Идентификатор пользователя-владельца кошелька
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    # Тип валюты кошелька
    currency: Mapped[CurrencyEnum]

    def withdraw(self, amount: Decimal):
        if self.balance < amount:
            raise ValueError(f"Not enough balance. Available balance: {self.balance} {self.currency}")
        self.balance -= amount

    def deposit(self, amount: Decimal):
        self.balance += amount


class Operation(Base):
    __tablename__ = 'operation'

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey('wallet.id'), nullable=False)
    target_wallet_id: Mapped[int | None] = mapped_column(ForeignKey('wallet.id'), nullable=True)
    type: Mapped[str]
    amount: Mapped[Decimal]
    currency: Mapped[CurrencyEnum]
    category: Mapped[str | None] = mapped_column(default=None)
    subcategory: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))