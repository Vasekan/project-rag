from typing import AsyncIterator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError


DB_URL = 'postgresql+asyncpg://postgres:admin@db:5432/users'

engine = create_async_engine(
    url=DB_URL,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[async_sessionmaker]:
    try:
        async_session = AsyncSessionLocal()
        async with async_session as session:
            yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()