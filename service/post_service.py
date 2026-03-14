from sqlalchemy.exc import IntegrityError
import asyncio
import base64

from db.repositories import UserRepository, PostRepository, PostLikeRepository, BlockRepository
from db.entities import PostLikeRelationship, PostModel

from exceptions import UserNotFoundError, PostNotFoundError, AccessDeniedError
from model import Post, PostRequest

from .image_utils import get_post_bytes, upload2post, delete_old_post


class PostService:
    user_repo: UserRepository
    post_repo: PostRepository
    like_repo: PostLikeRepository
    block_repo: BlockRepository

    def __init__(
            self,
            post_repo: PostRepository,
            user_repo: UserRepository,
            like_repo: PostLikeRepository,
            block_repo: BlockRepository
    ) -> None:
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.block_repo = block_repo

    @staticmethod
    async def post_to_object(post: PostModel, new_post: bool=False) -> Post:
        return Post(
            post_id=post.post_id,
            author_id=post.author_id,
            pub_time=post.pub_time,
            image=base64.b64encode(await get_post_bytes(post.post_id)),
            caption=post.caption,
            like_cnt=0 if new_post else post.like_cnt,
            comments=[] if new_post else [c.comment_id for c in post.comments]
        )

    async def get_post(self, post_id: int, user_id: int, author_id: int) -> Post:
        """
        Gets a post by its post ID
        :param post_id: post ID
        :param user_id: authenticated user ID
        :param author_id: author's user ID
        :return: the post, if it exists and the user is not blocked
        """
        if not (post := await self.post_repo.find_by_id(post_id, load_comments=True)):
            raise PostNotFoundError
        if await self.block_repo.find_by_id((author_id, user_id)):
            raise AccessDeniedError
        return await self.post_to_object(post)

    async def new_post(self, user_id: int, request: PostRequest) -> Post:
        """
        Creates a new post
        :param user_id: author ID
        :param request: post info (image and caption)
        :return: the post object
        """
        db_post = PostModel(author_id=user_id, caption=request.caption)
        try:
            db_post = await self.post_repo.save(db_post)
        except IntegrityError:
            raise UserNotFoundError

        await upload2post(db_post.post_id, request.image),
        return await self.post_to_object(db_post, new_post=True)

    async def delete_post(self, user_id: int, post_id: int) -> None:
        """
        Deletes a post
        :param user_id: author ID
        :param post_id: post ID
        """
        if db_post := await self.post_repo.find_by_id(post_id):
            if user_id != db_post.author_id:
                raise AccessDeniedError
            await asyncio.gather(
                self.post_repo.delete(db_post),
                delete_old_post(post_id)
            )

    async def get_user_posts(self, user_id: int, author_id: int) -> list[int]:
        """
        Get all posts from a specific user
        :param user_id: authenticated user ID
        :param author_id: target user ID
        :return: the list of posts as IDs
        """
        if await self.block_repo.find_by_id((author_id, user_id)):
            raise AccessDeniedError
        return await self.post_repo.find_by_author_id(author_id)

    async def get_user_feed(self, user_id: int, limit: int=100, page: int=0) -> list[int]:
        """
        Gets a user's feed (list of posts from followed accounts)
        :param user_id: user ID
        :param limit: number of posts to return
        :param page: page number for pagination
        :return: the user's feed as a list of references
        """
        if not  await self.user_repo.find_by_id(user_id):
            raise UserNotFoundError
        return await self.post_repo.find_feed(user_id, limit, limit * page)

    async def like_post(self, user_id: int, post_id: int) -> None:
        """
        Likes a post
        :param user_id: user ID
        :param post_id: post ID
        """
        if not await self.post_repo.find_by_id(post_id):
            raise PostNotFoundError
        try:
            await self.like_repo.save(PostLikeRelationship(user_id=user_id, post_id=post_id))
        except IntegrityError:
            raise UserNotFoundError

    async def unlike_post(self, user_id: int, post_id: int) -> None:
        """
        Unlikes a post
        :param user_id: user ID
        :param post_id: post ID
        """
        await self.like_repo.delete(PostLikeRelationship(user_id=user_id, post_id=post_id))
        if not await self.post_repo.find_by_id(post_id):
            raise PostNotFoundError

    async def get_post_likes(self, user_id: int, post_id: int) -> list[int]:
        """
        Gets a post's likes (users who liked the post)
        :param user_id: author ID
        :param post_id: user ID
        :return: the post's likes as a list of references
        """
        if not (post := await self.post_repo.find_by_id(post_id)):
            raise PostNotFoundError
        if user_id != post.author_id:
            raise AccessDeniedError
        return [
            like.user_id
            for like in await self.like_repo.find_by_post_id(post_id)
        ]

    async def is_liked(self, user_id: int, post_id: int) -> bool:
        """
        Checks whether a post was liked by the user
        :param user_id: user ID
        :param post_id: post ID
        :return: whether the post was liked by the user or not
        """
        return user_id in [
            like.user_id
            for like in await self.like_repo.find_by_post_id(post_id)
        ]
