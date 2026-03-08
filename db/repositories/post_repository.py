from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from ..entities import PostModel, FollowingRelationship

from .db_repository import DBRepository, T


class PostRepository(DBRepository[PostModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PostModel)

    async def find_by_id(self, post_id: int, load_comments: bool = False) -> PostModel | None:
        if load_comments:
            return await self.session.scalar(
                select(PostModel).options(selectinload(PostModel.comments)).where(PostModel.post_id == post_id)
            )
        return await self.session.scalar(select(PostModel).where(PostModel.post_id == post_id))

    async def find_feed(self, user_id: int, limit: int, offset: int) -> list[int]:
        """
        Builds a user's home page feed (list of posts by followed users)
        :param user_id: user ID
        :param limit: max number of posts to return
        :param offset: offset for pagination
        :return: the list of posts as post IDs in descending chronological order
        """
        return list((await self.session.scalars(
            select(PostModel.post_id)
                .join(FollowingRelationship, FollowingRelationship.following_id == PostModel.author_id)
                .where(FollowingRelationship.follower_id == user_id)
                .order_by(PostModel.pub_time.desc())
                .limit(limit)
                .offset(offset)
        )).all())
