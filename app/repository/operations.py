from datetime import datetime
from decimal import Decimal
from app.models import Operation
from sqlalchemy.orm import Session

from app.enum import CurrencyEnum


def create_operation(
        db: Session,
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
    db.flush()
    return operation

def get_operations_list(
    db: Session,
    wallets_ids: list[int],
    date_from: datetime | None,
    date_to: datetime | None,
) -> list[Operation]:
    query = db.query(Operation).filter(Operation.wallet_id.in_(wallets_ids))

    if date_from:
        query = query.filter(Operation.date >= date_from)

    if date_to:
        query = query.filter(Operation.date <= date_to)

    return query.all()