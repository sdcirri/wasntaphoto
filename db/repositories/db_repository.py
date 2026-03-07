from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Generic, TypeVar
from abc import ABC, abstractmethod


T = TypeVar('T')


class DBRepository(ABC, Generic[T]):
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @abstractmethod
    async def find_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, _id: Any) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, obj: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj: T) -> None:
        raise NotImplementedError
