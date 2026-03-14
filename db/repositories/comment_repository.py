from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..entities import CommentModel

from .db_repository import DBRepository


class CommentRepository(DBRepository[CommentModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CommentModel)

    async def find_by_id(self, comment_id: int) -> CommentModel | None:
        return await self.session.scalar(select(CommentModel).where(
            CommentModel.comment_id == comment_id
        ))
