from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..entities import CommentLikeRelationship

from .db_repository import DBRepository


class CommentLikeRepository(DBRepository[CommentLikeRelationship]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CommentLikeRelationship)

    async def find_by_id(self, user_comment_ids: tuple[int, int]) -> CommentLikeRelationship | None:
        user_id, comment_id = user_comment_ids
        return await self.session.scalar(select(CommentLikeRelationship).where(
            CommentLikeRelationship.user_id == user_id,
            CommentLikeRelationship.comment_id == comment_id
        ))

    async def find_by_comment_id(self, comment_id: int) -> list[CommentLikeRelationship]:
        return list((await self.session.scalars(
            select(CommentLikeRelationship).where(CommentLikeRelationship.comment_id == comment_id)
        )).all())
