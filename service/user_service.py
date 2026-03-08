from sqlalchemy.exc import IntegrityError
import asyncio

from db.repositories import UserRepository, FollowRepository, BlockRepository
from db.entities import UserModel, FollowingRelationship, BlockRelationship

from exceptions import UserNotFoundError, UsernameAlreadyTakenError, SelfFollowError
from model import UserAccount

from image_utils import get_propic_bytes, upload2propic


class UserService:
    user_repo: UserRepository
    follow_repo: FollowRepository
    block_repo: BlockRepository

    def __init__(
            self, user_repo: UserRepository,
            follow_repo: FollowRepository,
            block_repo: BlockRepository
    ) -> None:
        self.user_repo = user_repo
        self.follow_repo = follow_repo
        self.block_repo = block_repo

    @staticmethod
    async def user_to_object(db_user: UserModel) -> UserAccount:
        return UserAccount(
            user_id=db_user.user_id,
            username=db_user.username,
            propic=await get_propic_bytes(db_user.user_id),
            followers_cnt=db_user.followers_cnt,
            following_cnt=db_user.following_cnt,
            posts=[p.post_id for p in db_user.posts]
        )

    async def get_user(self, user_id: int) -> UserAccount:
        """
        Retrieves the user info
        :param user_id: user ID
        :return: the user info, if it exists and the requester isn't blocked by them
        """
        if not (db_user := await self.user_repo.find_by_id(user_id, load_posts=True)):
            raise UserNotFoundError
        return await self.user_to_object(db_user)

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
        return list(await asyncio.gather(*[self.user_to_object(u) for u in users]))

    async def get_following(self, user_id: int) -> list[UserAccount]:
        """
        Retrieves all users followed by the user
        :param user_id: user ID
        :return: the followed list
        """
        users = await self.user_repo.find_by_follower(user_id)
        return list(await asyncio.gather(*[self.user_to_object(u) for u in users]))

    async def get_blocked(self, user_id: int) -> list[UserAccount]:
        """
        Retrieves all users blocked by the user
        :param user_id: user ID
        :return: the blocked list
        """
        users = await self.user_repo.find_by_blocker(user_id)
        return list(await asyncio.gather(*[self.user_to_object(u) for u in users]))

    async def set_propic(self, user_id: int, uploaded_image: bytes) -> None:
        """
        Sets the user's profile picture
        :param user_id: user ID
        :param uploaded_image: the uploaded image to set
        """
        if not (user := await self.user_repo.find_by_id(user_id)):
            raise UserNotFoundError
        await upload2propic(user.user_id, uploaded_image)

    async def follow(self, user_id: int, to_follow_id: int) -> None:
        """
        Follows the user
        :param user_id: user ID of the user who wants to follow
        :param to_follow_id: user ID of the user to be followed
        """
        if user_id == to_follow_id:
            raise SelfFollowError
        if not await self.user_repo.find_by_id(user_id):
            raise UserNotFoundError
        if not await self.user_repo.find_by_id(to_follow_id):
            raise UserNotFoundError

        await self.follow_repo.save(
            FollowingRelationship(follower_id=user_id, following_id=to_follow_id)
        )


    async def unfollow(self, user_id: int, to_unfollow_id: int) -> None:
        """
        Unfollows the user
        :param user_id: user ID of the user who wants to unfollow
        :param to_unfollow_id: user ID of the user to be unfollowed
        """
        if user_id == to_unfollow_id:
            raise SelfFollowError
        if not await self.user_repo.find_by_id(user_id):
            raise UserNotFoundError
        if not await self.user_repo.find_by_id(to_unfollow_id):
            raise UserNotFoundError

        if rel := await self.follow_repo.find_by_id((user_id, to_unfollow_id)):
            await self.follow_repo.delete(rel)

    async def remove_follower(self, user_id: int, to_remove_id: int) -> None:
        """
        Removes a user from the user's followers
        :param user_id: user ID
        :param to_remove_id: follower to be removed
        """
        if user_id == to_remove_id:
            raise SelfFollowError
        if not await self.user_repo.find_by_id(user_id):
            raise UserNotFoundError
        if not await self.user_repo.find_by_id(to_remove_id):
            raise UserNotFoundError

        if rel := await self.follow_repo.find_by_id((to_remove_id, user_id)):
            await self.follow_repo.delete(rel)

    async def block_user(self, user_id: int, to_block_id: int) -> None:
        """
        Blocks a user, also removing the respective follow relationships
        :param user_id: user ID
        :param to_block_id: user ID of the user to be blocked
        """
        if user_id == to_block_id:
            raise SelfFollowError
        if not await self.user_repo.find_by_id(user_id):
            raise UserNotFoundError
        if not await self.user_repo.find_by_id(to_block_id):
            raise UserNotFoundError

        frel1, frel2 = await asyncio.gather(
            self.follow_repo.find_by_id((user_id, to_block_id)),
            self.follow_repo.find_by_id((to_block_id, user_id))
        )

        await asyncio.gather(
            self.block_repo.save(
                BlockRelationship(blocker_id=user_id, blocked_id=to_block_id)
            ),
            self.follow_repo.delete(frel1) if frel1 else asyncio.sleep(0),
            self.follow_repo.delete(frel2) if frel2 else asyncio.sleep(0)
        )

    async def unblock_user(self, user_id: int, to_unblock_id: int) -> None:
        """
        Unblocks a previously blocked user
        :param user_id: user ID
        :param to_unblock_id: user ID of the user to be unblocked
        """
        if user_id == to_unblock_id:
            raise SelfFollowError
        if not await self.user_repo.find_by_id(user_id):
            raise UserNotFoundError
        if not await self.user_repo.find_by_id(to_unblock_id):
            raise UserNotFoundError

        if rel := await self.block_repo.find_by_id((user_id, to_unblock_id)):
            await self.block_repo.delete(rel)
