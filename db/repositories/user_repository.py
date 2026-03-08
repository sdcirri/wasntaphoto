from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from ..entities import UserModel, FollowingRelationship, BlockRelationship

from .db_repository import DBRepository


class UserRepository(DBRepository[UserModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserModel)

    async def find_by_id(self, user_id: int, load_posts: bool = False) -> UserModel | None:
        if load_posts:
            return await self.session.scalar(
                select(UserModel).options(selectinload(UserModel.posts)).where(UserModel.user_id == user_id)
            )
        return await self.session.scalar(select(UserModel).where(UserModel.user_id == user_id))

    async def find_by_username(self, username: str) -> UserModel | None:
        return await self.session.scalar(select(UserModel).where(UserModel.username == username))

    async def find_by_follower(self, follower_id: int) -> list[UserModel]:
        return list((await self.session.scalars(
            select(UserModel)
                .join(FollowingRelationship, FollowingRelationship.following_id == UserModel.user_id)
                .where(FollowingRelationship.follower_id == follower_id)
        )).all())

    async def find_by_following(self, following_id: int) -> list[UserModel]:
        return list((await self.session.scalars(
            select(UserModel)
                .join(FollowingRelationship, FollowingRelationship.follower_id == UserModel.user_id)
                .where(FollowingRelationship.following_id == following_id)
        )).all())

    async def find_by_blocker(self, blocker_id: int) -> list[UserModel]:
        return list((await self.session.scalars(
            select(UserModel)
                .join(BlockRelationship, BlockRelationship.blocked_id == UserModel.user_id)
                .where(BlockRelationship.blocker_id == blocker_id)
        )).all())
