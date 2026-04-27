from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.enum import CurrencyEnum
from app.models import Wallet


async def get_wallet_by_name(db: AsyncSession, user_id: int, wallet_name: str) -> Wallet:
    result = await db.execute(
        select(Wallet).where(
            Wallet.name == wallet_name,
            Wallet.user_id == user_id
        )
    )
    return result.scalars().first()

async def get_all_wallets(db: AsyncSession, user_id: int) -> list[Wallet]:
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user_id
        )
    )
    return result.scalars().all()


async def create_wallet(db: AsyncSession, user_id: int, wallet_name: str, amount: Decimal, currency: CurrencyEnum) -> Wallet:
    wallet = Wallet(name=wallet_name, balance=amount, user_id=user_id, currency=currency)
    db.add(wallet)
    await db.flush() # Применение изменений к базе данных без сохранения транзакции
    return wallet

async def get_wallet_by_id(db: AsyncSession, user_id: int, wallet_id: int) -> Wallet | None:
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user_id,
            Wallet.id == wallet_id
        )
    )
    return result.scalars().first()