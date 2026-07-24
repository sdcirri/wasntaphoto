from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from typing import AsyncGenerator
from fastapi import Request
from os import getenv

from db.engine import get_engine


def get_engine_from_env() -> AsyncEngine:
    database_url = getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL is not set, exiting ...')

    return get_engine(database_url)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
