from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy import text

from typing import Coroutine, Any, Callable, AsyncIterator, Generator
from testcontainers.postgres import PostgresContainer
from pathlib import Path
from minio import Minio
from io import BytesIO
import pytest_asyncio
import pytest
import os

from db.repositories import UserRepository, PostRepository, CommentRepository
from db.entities import UserModel, PostModel, CommentModel

from service.storage_service import StorageService
from service.auth_service import AuthService
from service.image_utils import upload2post

INITDB_DIR = Path(__file__).resolve().parents[2] / 'initdb'


@pytest.fixture(scope='session')
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer(
            'postgres:18',
            username='wasntaphoto',
            password='wasntaphoto',
            dbname='wasntaphoto',
    ) as postgres:
        postgres.with_volume_mapping(str(INITDB_DIR), '/docker-entrypoint-initdb.d')
        postgres.start()
        os.environ['DATABASE_URL'] = postgres.get_connection_url().replace(
            "postgresql+psycopg2://", "postgresql+psycopg://"
        )
        yield postgres


def _async_url(container: PostgresContainer) -> str:
    # testcontainers returns postgresql+psycopg2://...
    return container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+psycopg://"
    )


@pytest_asyncio.fixture(scope='session')
async def test_engine(postgres_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(_async_url(postgres_container), pool_pre_ping=True)
    os.environ['DATABASE_URL'] = _async_url(postgres_container)
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config('alembic.ini')
    command.upgrade(alembic_cfg, 'head')

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True, scope='function')
async def test_db_session_factory(
        test_engine: AsyncEngine
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    yield async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest_asyncio.fixture(autouse=True, scope='function')
async def _clean_db(test_engine: AsyncEngine) -> AsyncIterator[None]:
    """
    Wipe all data after each test
    """
    yield
    async with test_engine.begin() as conn:
        await conn.execute(text('''
            TRUNCATE TABLE
              wasntaphoto.comment_like_relationship,
              wasntaphoto.post_like_relationship,
              wasntaphoto.comments,
              wasntaphoto.user_sessions,
              wasntaphoto.posts,
              wasntaphoto.following,
              wasntaphoto.blocking,
              wasntaphoto.users
            RESTART IDENTITY CASCADE
        '''))


@pytest_asyncio.fixture
async def user_factory(test_db_session_factory: async_sessionmaker[AsyncSession]) -> Callable[[str, str], Coroutine[Any, Any, UserModel]]:
    async def _create_user(username: str, password: str) -> UserModel:
        async with test_db_session_factory() as session:
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
async def post_factory(
        test_db_session_factory: async_sessionmaker[AsyncSession],
        minio_client: Minio
) -> Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]]:
    async def _create_post(author_id: int, raw_image: bytes, caption: str | None) -> PostModel:
        async with test_db_session_factory() as session:
            post_repo = PostRepository(session)
            db_post = PostModel(
                author_id=author_id,
                caption=caption
            )
            db_post = await post_repo.save(db_post)
            await session.commit()

            with BytesIO(upload2post(raw_image)) as img:
                minio_client.put_object(
                    StorageService.POST_BUCKET,
                    f'{db_post.post_id}.jpg',
                    img,
                    length=-1,
                    part_size=10 * 1024 * 1024,
                    content_type='image/jpeg'
                )
            return db_post

    return _create_post


@pytest_asyncio.fixture
async def comment_factory(test_db_session_factory: async_sessionmaker[AsyncSession]) -> Callable[[int, int, str], Coroutine[Any, Any, CommentModel]]:
    async def _create_comment(author_id: int, post_id: int, content: str) -> CommentModel:
        async with test_db_session_factory() as session:
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


@pytest_asyncio.fixture
async def next_unused_user_id(test_db_session_factory: async_sessionmaker[AsyncSession]) -> int:
    """
    Returns the next unused user ID. Useful when a
    nonexisting user ID is needed
    """
    async with test_db_session_factory() as session:
        user_repo = UserRepository(session)
        users = await user_repo.find_all()
        if len(users) == 0:
            return 0
        return 1 + max(users, key=lambda u: u.user_id).user_id


@pytest_asyncio.fixture
async def next_unused_comment_id(test_db_session_factory: async_sessionmaker[AsyncSession]) -> int:
    """
    Returns the next unused comment ID. Useful when a
    nonexisting user ID is needed
    """
    async with test_db_session_factory() as session:
        comment_repo = CommentRepository(session)
        comments = await comment_repo.find_all()
        if len(comments) == 0:
            return 0
        return 1 + max(comments, key=lambda c: c.comment_id).comment_id
