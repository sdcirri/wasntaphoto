from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import BigInteger, event
from sqlalchemy.pool import StaticPool

from typing import Coroutine, Any, Callable, AsyncGenerator
from difflib import SequenceMatcher
import pytest_asyncio
import httpx
import os

os.environ['DATABASE_URL'] = 'postgresql+psycopg://'
os.environ['WASA_STORAGE_ROOT'] = '/tmp/wasa'
os.makedirs(os.environ['WASA_STORAGE_ROOT'], exist_ok=True)

from db.repositories import UserRepository
from db.entities import UserModel
from db.engine import Base

from service.image_utils import DEFAULT_PROPIC
from service.auth_service import AuthService

from providers.db import get_db_session

from app import app


@compiles(BigInteger, 'sqlite')
def _compile_bigint_sqlite(_type, _compiler, **_kwargs) -> str:
    return 'INTEGER'


def _similarity(left: str | None, right: str | None) -> float:
    return SequenceMatcher(None, left or '', right or '').ratio()


TEST_ENGINE = create_async_engine(
    'sqlite+aiosqlite:///:memory:',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(TEST_ENGINE, expire_on_commit=False, class_=AsyncSession)


@event.listens_for(TEST_ENGINE.sync_engine, 'connect')
def _configure_sqlite(dbapi_connection, _connection_record) -> None:
    dbapi_connection.execute("ATTACH DATABASE ':memory:' AS wasntaphoto")
    dbapi_connection.execute('PRAGMA foreign_keys=ON')
    dbapi_connection.create_function('similarity', 2, _similarity)


with open(DEFAULT_PROPIC, 'wb') as f:
    # One pixel JPEG.
    f.write(bytes.fromhex(
        'ffd8ffe000104a46494600010100000100010000'
        'ffda0008010100003f00'
        'ffd9'
    ))


@pytest_asyncio.fixture(autouse=True)
async def _sqlite_database() -> AsyncGenerator[None, None]:
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def _get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _get_test_db_session
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_factory() -> Callable[[str, str], Coroutine[Any, Any, UserModel]]:
    async def _create_user(username: str, password: str) -> UserModel:
        async with TestSessionLocal() as session:
            user_repo = UserRepository(session)
            db_user = UserModel(
                username=username,
                password=AuthService.ph.hash(password)
            )
            db_user = await user_repo.save(db_user)
            await session.commit()
            return db_user

    return _create_user


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client
