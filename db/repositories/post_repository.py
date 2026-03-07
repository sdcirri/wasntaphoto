from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..entities import PostModel

from .db_repository import DBRepository, T


class PostRepository(DBRepository[PostModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PostModel)

    async def find_by_id(self, post_id: int) -> PostModel | None:
        return await self.session.scalar(select(PostModel).where(PostModel.post_id == post_id))
