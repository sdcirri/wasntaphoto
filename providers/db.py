from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from os import getenv

from db.engine import get_sessionmaker, get_engine


database_url = getenv('DATABASE_URL')
if not database_url:
    raise RuntimeError('DATABASE_URL is not set, exiting ...')

engine = get_engine(getenv('DATABASE_URL'))
SessionLocal = get_sessionmaker(engine)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
