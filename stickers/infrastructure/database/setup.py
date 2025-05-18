from typing import AsyncContextManager, Callable

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from stickers.config import DbConfig, Config
from stickers.infrastructure.database.models import Base

from stickers.infrastructure.database.repo.requests import RequestsRepo


async def create_session_pool(db: DbConfig, echo=False) -> Callable[[], AsyncContextManager[AsyncSession]]:
    engine = create_async_engine(
        db.construct_sqlalchemy_url(),
        query_cache_size=1200,
        pool_size=10,
        max_overflow=200,
        future=True,
        echo=echo,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

    session_pool = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    return session_pool


async def get_repo(config: Config) -> RequestsRepo:
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        return RequestsRepo(session)

