from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..entities import FollowingRelationship

from .db_repository import DBRepository


class FollowRepository(DBRepository[FollowingRelationship]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FollowingRelationship)

    async def find_by_id(self, follower_following_id: tuple[int, int]) -> FollowingRelationship | None:
        follower_id, following_id = follower_following_id
        return await self.session.scalar(
            select(FollowingRelationship).where(
                FollowingRelationship.follower_id == follower_id,
                FollowingRelationship.following_id == following_id
            )
        )
