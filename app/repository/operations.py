from datetime import datetime
from decimal import Decimal
from app.models import Operation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.enum import CurrencyEnum


async def create_operation(
        db: AsyncSession,
        wallet_id: int,
        type: str,
        amount: Decimal,
        currency: CurrencyEnum,
        target_wallet_id: int | None = None,
        category: str | None = None,
        subcategory: str | None = None,
) -> Operation:
    operation = Operation(
        wallet_id=wallet_id,
        target_wallet_id=target_wallet_id,
        type=type,
        amount=amount,
        currency=currency,
        category=category,
        subcategory=subcategory
    )
    db.add(operation)
    await db.flush()
    return operation

async def get_operations_list(
    db: AsyncSession,
    wallets_ids: list[int],
    date_from: datetime | None,
    date_to: datetime | None,
) -> list[Operation]:
    query = select(Operation).where(Operation.wallet_id.in_(wallets_ids))

    if date_from:
        query = query.where(Operation.created_at >= date_from)

    if date_to:
        query = query.where(Operation.created_at <= date_to)

    result = await db.execute(query)

    return result.scalars().all()