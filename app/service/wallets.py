from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.enum import CurrencyEnum
from app.models import User
from app.schemas import CreateWalletRequest, WalletResponse, TotalBalance
from app.repository import wallets as wallets_repository
from app.service import exchange_service


async def get_total_balance(db: Session, current_user: User) -> TotalBalance:
    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    if not wallets:
        raise HTTPException(status_code=404, detail="No wallets")
    total = Decimal(0)
    for wallet in wallets:
        rate = Decimal(1)
        if wallet.currency != CurrencyEnum.RUB:
            rate = await exchange_service.get_exchange_rate(wallet.currency, CurrencyEnum.RUB)
        total += wallet.balance * rate
    return TotalBalance(total_balance=total)



def create_wallet(db: Session, current_user: User, wallet: CreateWalletRequest) -> WalletResponse:
    # Проверяем существует ли уже такой кошелёк
    wallet_cheak = wallets_repository.get_wallet_by_name(db, current_user.id, wallet.name)
    if wallet_cheak:
        raise HTTPException(
            status_code=400,
            detail=f"Wallet {wallet.name} already exists"
        )
    # Создаём новый кошелёк с начальным балансом
    wallet = wallets_repository.create_wallet(db, current_user.id, wallet.name, wallet.initial_balance, wallet.currency)
    db.commit()
    return WalletResponse.model_validate(wallet)


def get_all_wallets(db: Session, current_user: User) -> list[WalletResponse]:
    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    return [WalletResponse.model_validate(wallet) for wallet in wallets]
