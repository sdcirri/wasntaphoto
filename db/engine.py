from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData


class Base(DeclarativeBase):
    metadata = MetaData(schema='wasntaphoto')


def get_engine(conninfo: str) -> AsyncEngine:
    return create_async_engine(
        conninfo,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )


def get_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
