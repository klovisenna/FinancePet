from typing import AsyncGenerator

from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import users as users_repository
from app.database import AsyncSessionLocal
from app.models import User

security = HTTPBearer()

# Функция для получения сессии базы данных через dependency injection в FastAPI
async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                     db: AsyncSession = Depends(get_db)) -> User:
    login = credentials.credentials

    user = await users_repository.get_user_by_login(db, login)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user