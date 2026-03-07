from sqlalchemy import select

from db.entities import UserModel, FollowingRelationship, BlockRelationship

from .db_repository import DBRepository


class UserRepository(DBRepository):
    """
    Repository for user accounts
    """

    async def find_all(self) -> list[UserModel]:
        return list((await self.session.scalars(select(UserModel))).all())

    async def find_by_id(self, user_id: int) -> UserModel | None:
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

    async def save(self, user: UserModel) -> None:
        await self.session.merge(user)

    async def delete(self, user: UserModel) -> None:
        await self.session.delete(user)
