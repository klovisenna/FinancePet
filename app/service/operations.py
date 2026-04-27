from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import OperationType
from app.models import User
from app.repository import wallets as wallets_repository
from app.repository import operations as operations_repository
from app.schemas import IncomeRequest, ExpenseRequest, TransactionRequest, OperationResponse
from app.service import exchange_service


async def add_income(db: AsyncSession, current_user: User, income: IncomeRequest) -> OperationResponse:
    # Существует ли такой кошелёк
    wallet = await wallets_repository.get_wallet_by_name(db, current_user.id, income.wallet_name)
    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {income.wallet_name} not found"
        )
    wallet.deposit(income.amount)
    operation = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.INCOME,
        amount=income.amount,
        currency=wallet.currency,
        category=income.description
    )
    await db.commit()
    return OperationResponse.model_validate(operation)


async def add_expense(db: AsyncSession, current_user: User, expense: ExpenseRequest) -> OperationResponse:
    wallet = await wallets_repository.get_wallet_by_name(db, current_user.id, expense.wallet_name)
    if not wallet:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {expense.wallet_name} not found"
        )
    wallet.withdraw(expense.amount)
    operation = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.EXPENSE,
        amount=expense.amount,
        currency=wallet.currency,
        category=expense.description
    )
    await db.commit()
    return OperationResponse.model_validate(operation)


async def get_operations_list(
    db: AsyncSession,
    current_user: User,
    wallet_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None
) -> list[OperationResponse]:
    if wallet_id:
        wallet = await wallets_repository.get_wallet_by_id(db, current_user.id, wallet_id)
        if not wallet:
            raise HTTPException(
                status_code=404,
                detail=f"Wallet {wallet_id} not found"
            )
        wallets_ids = [wallet.id]
    else:
        wallets = await wallets_repository.get_all_wallets(db, current_user.id)
        wallets_ids = [wallet.id for wallet in wallets]

    operations = await operations_repository.get_operations_list(
        db,
        wallets_ids,
        date_from,
        date_to,
    )
    return [OperationResponse.model_validate(operation) for operation in operations]

async def transaction(db: AsyncSession, current_user: User, transaction: TransactionRequest) -> list[OperationResponse]:
    wallet_from = await wallets_repository.get_wallet_by_name(db, current_user.id, transaction.from_wallet_name)
    wallet_to = await wallets_repository.get_wallet_by_name(db, current_user.id, transaction.to_wallet_name)
    if not wallet_from:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {transaction.from_wallet_name} not found"
        )
    if not wallet_to:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet {transaction.to_wallet_name} not found"
        )

    target_amount = round(transaction.amount, 2)
    if wallet_from.currency != wallet_to.currency:
        exchange_rate = await exchange_service.get_exchange_rate(wallet_from.currency, wallet_to.currency)
        target_amount = round(transaction.amount * exchange_rate, 2)
    wallet_from.withdraw(transaction.amount)
    operation_from = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet_from.id,
        target_wallet_id=wallet_to.id,
        type=OperationType.EXPENSE,
        amount=transaction.amount,
        currency=wallet_from.currency,
        category=transaction.description
    )
    wallet_to.deposit(target_amount)
    operation_to = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet_to.id,
        target_wallet_id=wallet_from.id,
        type=OperationType.INCOME,
        amount=target_amount,
        currency=wallet_to.currency,
        category=transaction.description
    )
    return [OperationResponse.model_validate(operation_from), OperationResponse.model_validate(operation_to)]