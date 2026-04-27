from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db, get_current_user
from app.models import User
from app.service import operations as operations_service

from app.schemas import IncomeRequest, ExpenseRequest, TransactionRequest, OperationResponse

router = APIRouter()

@router.post("/operations/income", response_model=OperationResponse)
async def add_income(income: IncomeRequest, db: AsyncSession = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return await operations_service.add_income(db, current_user, income)


@router.post("/operations/expense", response_model=OperationResponse)
async def add_expense(expense: ExpenseRequest, db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return await operations_service.add_expense(db, current_user, expense)

@router.get("/operations", response_model=list[OperationResponse])
async def get_operations_list(
        wallet_id: int | None = Query(None),
        date_from: datetime | None = Query(None),
        date_to: datetime | None = Query(None),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    return await operations_service.get_operations_list(db, user, wallet_id, date_from, date_to)

@router.post("/operations/transaction", response_model=list[OperationResponse])
async def add_transaction(
    transaction: TransactionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return await operations_service.transaction(db, current_user, transaction)