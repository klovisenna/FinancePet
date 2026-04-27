from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Numeric, String, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enum import CurrencyEnum


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), unique=True)

class Wallet(Base):
    __tablename__ = 'wallet'
    #Уникальный идентификатор кошелька т.е. первичный ключ
    id: Mapped[int] = mapped_column(primary_key=True)
    # Название кошелька
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Баланс кошелька. Используется Decimal для точных вычислений
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    # Идентификатор пользователя-владельца кошелька
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    # Тип валюты кошелька
    currency: Mapped[CurrencyEnum] = mapped_column(Enum(CurrencyEnum, name="currency_enum"))

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
    type: Mapped[str] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(Enum(CurrencyEnum, name="currency_enum"))
    category: Mapped[str | None] = mapped_column(String(100), default=None)
    subcategory: Mapped[str | None] = mapped_column(String(100), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))