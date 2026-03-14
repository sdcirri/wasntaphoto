from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..entities import PostLikeRelationship

from .db_repository import DBRepository


class PostLikeRepository(DBRepository[PostLikeRelationship]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PostLikeRelationship)

    async def find_by_id(self, user_post_ids: tuple[int, int]) -> PostLikeRelationship | None:
        user_id, post_id = user_post_ids
        return await self.session.scalar(select(PostLikeRelationship).where(
            PostLikeRelationship.user_id == user_id,
            PostLikeRelationship.post_id == post_id
        ))

    async def find_by_post_id(self, post_id: int) -> list[PostLikeRelationship]:
        return list((await self.session.scalars(
            select(PostLikeRelationship).where(PostLikeRelationship.post_id == post_id)
        )).all())
