from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.wallets import router as wallets_router
from app.api.v1.operations import router as operations_router
from app.api.v1.users import router as users_router
from app.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    #Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


# Инициализация FastAPI приложения
app = FastAPI(lifespan=lifespan)

app.include_router(wallets_router, prefix="/api/v1", tags=["wallets"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
