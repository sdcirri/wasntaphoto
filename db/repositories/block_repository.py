from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..entities import BlockRelationship

from .db_repository import DBRepository


class BlockRepository(DBRepository[BlockRelationship]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BlockRelationship)

    async def find_by_id(self, blocker_blocked_id: tuple[int, int]) -> BlockRelationship | None:
        blocker_id, blocked_id = blocker_blocked_id
        return await self.session.scalar(
            select(BlockRelationship).where(
                BlockRelationship.blocker_id == blocker_id,
                BlockRelationship.blocked_id == blocked_id
            )
        )
