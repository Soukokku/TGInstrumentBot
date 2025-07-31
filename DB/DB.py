from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from DB.models import Base
<<<<<<< HEAD
from config import DATABASE_URL
=======

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/Tg"
>>>>>>> 2b43ccfb846ddfd640f886d374a935c1c06660cf

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
