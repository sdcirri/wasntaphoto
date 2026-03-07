from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import MetaData


class Base(DeclarativeBase):
    metadata = MetaData(schema='wasntaphoto')


def get_engine(pg_user: str, pg_pass: str|None, pg_host: str, pg_port: int, pg_dbname: str) -> AsyncEngine:
    return create_async_engine(
        f'postgresql+psycopg://{pg_user}:{pg_pass or ""}@{pg_host}:{pg_port}/{pg_dbname}',
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )


def AsyncSessionLocal(engine: AsyncEngine) -> sessionmaker[AsyncSession]:
    return sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
