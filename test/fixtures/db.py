from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import BigInteger, event
from sqlalchemy.pool import StaticPool

from typing import Coroutine, Any, Callable, AsyncIterator
from difflib import SequenceMatcher
import pytest_asyncio
import pytest

from db.repositories import UserRepository, PostRepository, CommentRepository
from db.entities import UserModel, PostModel, CommentModel
from db.engine import Base

from service.auth_service import AuthService
from service.image_utils import upload2post
import providers.db as db_provider


def _similarity(left: str | None, right: str | None) -> float:
    return SequenceMatcher(None, left or '', right or '').ratio()


@compiles(BigInteger, 'sqlite')
def _compile_bigint_sqlite(_type, _compiler, **_kwargs) -> str:
    return 'INTEGER'


@pytest_asyncio.fixture(autouse=True, scope='function')
async def _sqlite_database(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    test_engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    test_session_factory = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    @event.listens_for(test_engine.sync_engine, 'connect')
    def _configure_sqlite(
            dbapi_connection: object,
            _connection_record: object,
    ) -> None:
        dbapi_connection.execute('ATTACH DATABASE \':memory:\' AS wasntaphoto')
        dbapi_connection.execute('PRAGMA foreign_keys=ON')
        dbapi_connection.create_function('similarity', 2, _similarity)

    try:
        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        monkeypatch.setattr(
            db_provider,
            "SessionLocal",
            test_session_factory,
        )

        yield test_session_factory
    finally:
        await test_engine.dispose()


@pytest_asyncio.fixture
async def user_factory(_sqlite_database: async_sessionmaker[AsyncSession]) -> Callable[[str, str], Coroutine[Any, Any, UserModel]]:
    async def _create_user(username: str, password: str) -> UserModel:
        async with _sqlite_database() as session:
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
async def post_factory(_sqlite_database: async_sessionmaker[AsyncSession]) -> Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]]:
    async def _create_post(author_id: int, raw_image: bytes, caption: str | None) -> PostModel:
        async with _sqlite_database() as session:
            post_repo = PostRepository(session)
            db_post = PostModel(
                author_id=author_id,
                caption=caption
            )
            db_post = await post_repo.save(db_post)
            await session.commit()

            await upload2post(db_post.post_id, raw_image)
            return db_post

    return _create_post


@pytest_asyncio.fixture
async def comment_factory(_sqlite_database: async_sessionmaker[AsyncSession]) -> Callable[[int, int, str], Coroutine[Any, Any, CommentModel]]:
    async def _create_comment(author_id: int, post_id: int, content: str) -> CommentModel:
        async with _sqlite_database() as session:
            comment_repo = CommentRepository(session)
            db_comment = CommentModel(
                author_id=author_id,
                post_id=post_id,
                content=content
            )
            db_comment = await comment_repo.save(db_comment)
            await session.commit()

            return db_comment

    return _create_comment
