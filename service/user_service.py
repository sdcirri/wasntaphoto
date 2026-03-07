from sqlalchemy.exc import IntegrityError
import aiofiles
import asyncio
import os.path

from db.repositories import UserRepository
from db.entities import UserModel

from exceptions import UserNotFoundError, UsernameAlreadyTakenError
from model.user import UserAccount


STORAGE_ROOT, DEFAULT_PROPIC = 'propics/', 'propics/default.jpg'


class UserService:
    user_repo: UserRepository

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    @staticmethod
    async def get_propic_bytes(user_id: int) -> bytes:
        """
        Gets the user's propic. If not set, returns the default one
        :param user_id: user ID
        :return: the propic bytes
        """
        try:
            async with aiofiles.open(os.path.join(STORAGE_ROOT, f'{user_id}.jpg'), 'rb') as f:
                return await f.read()
        except FileNotFoundError:
            async with aiofiles.open(os.path.join(DEFAULT_PROPIC), 'rb') as f:
                return await f.read()

    async def to_object(self, db_user: UserModel) -> UserAccount:
        return UserAccount(
            user_id=db_user.user_id,
            username=db_user.username,
            propic=await self.get_propic_bytes(db_user.user_id),
            followers_cnt=db_user.followers_cnt,
            following_cnt=db_user.following_cnt,
            posts=db_user.posts
        )

    async def get_user(self, user_id: int) -> UserAccount:
        """
        Retrieves the user info
        :param user_id: user ID
        :return: the user info, if it exists and the requester isn't blocked by them
        """
        if not (db_user := await self.user_repo.find_by_id(user_id)):
            raise UserNotFoundError
        return await self.to_object(db_user)

    async def change_username(self, user_id: int, new_username: str) -> None:
        """
        Changes the user's username
        :param user_id: user ID
        :param new_username: picked new username
        """
        if not (user := await self.user_repo.find_by_id(user_id)):
            raise UserNotFoundError
        try:
            user.username = new_username
            await self.user_repo.save(user)
        except IntegrityError:
            raise UsernameAlreadyTakenError

    async def get_followers(self, user_id: int) -> list[UserAccount]:
        """
        Retrieves all the followers of the user
        :param user_id: user ID
        :return: the followers list
        """
        users = await self.user_repo.find_by_following(user_id)
        return list(await asyncio.gather(*[self.to_object(u) for u in users]))

    async def get_following(self, user_id: int) -> list[UserAccount]:
        """
        Retrieves all users followed by the user
        :param user_id: user ID
        :return: the followed list
        """
        users = await self.user_repo.find_by_follower(user_id)
        return list(await asyncio.gather(*[self.to_object(u) for u in users]))

    async def get_blocked(self, user_id: int) -> list[UserAccount]:
        """
        Retrieves all users blocked by the user
        :param user_id: user ID
        :return: the blocked list
        """
        users = await self.user_repo.find_by_blocker(user_id)
        return list(await asyncio.gather(*[self.to_object(u) for u in users]))

    async def follow(self, user_id: int, to_follow_id: int) -> None:
        pass

    async def unfollow(self, user_id: int, to_unfollow_id: int) -> None:
        pass

    async def remove_follower(self, user_id: int, to_remove_id: int) -> None:
        pass

    async def block_user(self, user_id: int, to_block_id: int) -> None:
        pass

    async def unblock_user(self, user_id: int, to_unblock_id: int) -> None:
        pass
