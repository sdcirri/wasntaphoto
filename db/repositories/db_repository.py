from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Any, Generic, TypeVar
from abc import ABC, abstractmethod


T = TypeVar('T')


class DBRepository(ABC, Generic[T]):
    session: AsyncSession
    model: type[T]

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    @abstractmethod
    async def find_by_id(self, _id: Any) -> T | None:
        raise NotImplementedError

    async def find_all(self) -> list[T]:
        return list((await self.session.scalars(select(self.model))).all())

    async def save(self, obj: T) -> None:
        await self.session.merge(obj)

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)
