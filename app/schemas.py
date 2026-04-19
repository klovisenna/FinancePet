from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.enum import CurrencyEnum
from app.models import Wallet


class BaseOperation(BaseModel):
    amount: Decimal
    description: str | None = Field(None, max_length=127)

    @field_validator("amount")
    def amount_validator(cls, v: Decimal) -> Decimal:
        # Проверка что значение больше нуля
        if v <= 0:
            raise ValueError("Amount must be positive")
        # Возвращаем если всё ок
        return v


class IncomeRequest(BaseOperation):
    wallet_name: str = Field(..., max_length=127)

    @field_validator("wallet_name")
    def wallet_name_validator(cls, v: str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        # Проверяем что строка не пустая
        if not v:
            raise ValueError("Wallet name is required")
        # Возвращаем очищенное значение
        return v


class ExpenseRequest(BaseOperation):
    wallet_name: str = Field(..., max_length=127)

    @field_validator("wallet_name")
    def wallet_name_validator(cls, v: str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        # Проверяем что строка не пустая
        if not v:
            raise ValueError("Wallet name is required")
        # Возвращаем очищенное значение
        return v


class TransactionRequest(BaseOperation):
    from_wallet_name: str = Field(..., max_length=127)
    to_wallet_name: str = Field(..., max_length=127)

    @field_validator("from_wallet_name", "to_wallet_name")
    def wallet_name_validator(cls, v: str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        # Проверяем что строка не пустая
        if not v:
            raise ValueError("Wallet name is required")
        # Возвращаем очищенное значение
        return v

    @model_validator(mode="after")
    def check_wallets_are_different(self):
        if self.from_wallet_name == self.to_wallet_name:
            raise ValueError("Wallets are the same")
        return self


class CreateWalletRequest(BaseModel):
    # Название кошелька - обязательное поле, максимум 127 символов
    name: str = Field(..., max_length=127)
    # Начальный баланс - необязательное поле, по умолчанию 0
    initial_balance: Decimal = 0
    # Тип валюты - необязательное поле, по умолчанию рубли
    currency: CurrencyEnum = CurrencyEnum.RUB

    @field_validator("name")
    def name_validator(cls, v: str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        # Проверяем что строка не пустая
        if not v:
            raise ValueError("Wallet name is required")
        # Возвращаем очищенное значение
        return v

    @field_validator("initial_balance")
    def balance_validator(cls, v: Decimal) -> Decimal:
        # Проверка что значение больше нуля
        if v < 0:
            raise ValueError("Initial balance cannot be negative")
        # Возвращаем если всё ок
        return v

# Модель для создания пользователя
class UserRequest(BaseModel):
    login: str = Field(..., max_length=127)


# Модель для ответа с информацией о пользователе
class UserResponse(UserRequest):
    # Настройка для автоматического создания атрибутов объекта из алхимической модели
    model_config = {"from_attributes": True}
    # Уникальный идентификатор пользователя
    id: int

class WalletResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    balance: Decimal
    currency: CurrencyEnum

class OperationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    wallet_id: int
    target_wallet_id: int | None
    type: str
    amount: Decimal
    currency: CurrencyEnum
    category: str | None
    subcategory: str | None
    created_at: datetime

class TotalBalance(BaseModel):
    total_balance: Decimal