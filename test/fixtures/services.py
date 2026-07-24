from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import AsyncIterator
from redis.asyncio import Redis
import pytest

from db.repositories import UserRepository, SessionRepository
from service import AuthService


@pytest.fixture
async def fake_auth_service(
        redis_client: Redis,
        test_db_session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AuthService]:
    async with test_db_session_factory() as db:
        yield AuthService(
            UserRepository(db),
            SessionRepository(db),
            redis_client
        )
