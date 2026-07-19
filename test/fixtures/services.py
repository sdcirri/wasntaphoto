from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from fakeredis.aioredis import FakeRedis
from typing import AsyncIterator
import pytest

from db.repositories import UserRepository, SessionRepository
from service import AuthService


@pytest.fixture
async def fake_auth_service(
        override_redis: FakeRedis,
        _sqlite_database: async_sessionmaker[AsyncSession]) -> AsyncIterator[AuthService]:
    async with _sqlite_database() as db:
        yield AuthService(
            UserRepository(db),
            SessionRepository(db),
            override_redis
        )
