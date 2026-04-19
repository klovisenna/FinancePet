from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.dependency import get_db, get_current_user
from app.models import User
from app.service import operations as operations_service

from app.schemas import IncomeRequest, ExpenseRequest, TransactionRequest, OperationResponse, WalletResponse

router = APIRouter()

@router.post("/operations/income", response_model=OperationResponse)
def add_income(income: IncomeRequest, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return operations_service.add_income(db, current_user, income)


@router.post("/operations/expense", response_model=OperationResponse)
def add_expense(expense: ExpenseRequest, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return operations_service.add_expense(db, current_user, expense)

@router.get("/operations", response_model=list[OperationResponse])
def get_operations_list(
        wallet_id: int | None = Query(None),
        date_from: datetime | None = Query(None),
        date_to: datetime | None = Query(None),
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return operations_service.get_operations_list(db, user, wallet_id, date_from, date_to)

@router.post("/operations/transaction", response_model=list[OperationResponse])
async def add_transaction(
    transaction: TransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return await operations_service.transaction(db, current_user, transaction)