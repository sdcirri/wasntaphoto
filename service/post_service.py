from sqlalchemy.exc import IntegrityError
import asyncio

from db.repositories import UserRepository, PostRepository, PostLikeRepository
from db.entities import PostLikeRelationship, PostModel

from exceptions import UserNotFoundError, PostNotFoundError, AccessDeniedError
from model import Post, PostRequest

from .image_utils import get_post_bytes, upload2post


class PostService:
    user_repo: UserRepository
    post_repo: PostRepository
    like_repo: PostLikeRepository

    def __init__(
            self,
            post_repo: PostRepository,
            user_repo: UserRepository,
            like_repo: PostLikeRepository
    ) -> None:
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo

    @staticmethod
    async def post_to_object(post: PostModel) -> Post:
        return Post(
            post_id=post.post_id,
            author_id=post.author_id,
            pub_time=post.pub_time,
            image=await get_post_bytes(post.post_id),
            caption=post.caption,
            like_cnt=post.like_cnt,
            comments=[c.comment_id for c in post.comments]
        )

    async def get_post(self, post_id: int) -> Post:
        """
        Gets a post by its post ID
        :param post_id: post ID
        :return: the post, if it exists
        """
        if not (post := await self.post_repo.find_by_id(post_id, load_comments=True)):
            raise PostNotFoundError
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

        _, post = await asyncio.gather(
            upload2post(db_post.post_id, request.image),
            self.post_to_object(db_post)
        )
        return post

    async def delete_post(self, user_id: int, post_id: int) -> None:
        """
        Deletes a post
        :param user_id: author ID
        :param post_id: post ID
        """
        if db_post := await self.post_repo.find_by_id(post_id):
            if user_id != db_post.author_id:
                raise AccessDeniedError
            await self.post_repo.delete(db_post)

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
