import asyncio
import base64

from db.repositories import UserRepository, PostRepository, PostLikeRepository, BlockRepository
from db.entities import PostLikeRelationship, PostModel

from exceptions import PostNotFoundError, AccessDeniedError
from model import Post, PostRequest

from .storage_service import StorageService
from .image_utils import upload2post


class PostService:
    user_repo: UserRepository
    post_repo: PostRepository
    like_repo: PostLikeRepository
    block_repo: BlockRepository
    storage_service: StorageService

    def __init__(
            self,
            post_repo: PostRepository,
            user_repo: UserRepository,
            like_repo: PostLikeRepository,
            block_repo: BlockRepository,
            storage_service: StorageService
    ) -> None:
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.block_repo = block_repo
        self.storage_service = storage_service

    async def post_to_object(self, post: PostModel, cached_img: bytes | None=None, new_post: bool=False) -> Post:
        """
        Builds a Post object for the API
        :param post: post DB object
        :param cached_img: the post image bytes if available (to avoid calling the storage bucket)
        :param new_post: whether the post is new or not (not to bother the DB with likes and comments aggregates)
        :return: the Post object
        """
        img = cached_img if cached_img is not None else await self.storage_service.get_post(post.post_id)
        assert img is not None, 'Post has no attached image!'

        return Post(
            post_id=post.post_id,
            author_id=post.author_id,
            pub_time=post.pub_time,
            image=base64.b64encode(img),
            caption=post.caption,
            like_cnt=0 if new_post else post.like_cnt,
            comments=[] if new_post else [c.comment_id for c in post.comments]
        )

    async def get_post(self, post_id: int, user_id: int, author_id: int) -> Post:
        """
        Gets a post by its post ID
        :param post_id: post ID
        :param user_id: authenticated user ID
        :param author_id: post author ID
        :return: the post, if it exists and the user is not blocked
        """
        if not (post := await self.post_repo.find_by_id(post_id, load_comments=True)):
            raise PostNotFoundError
        if post.author_id != author_id:
            raise PostNotFoundError
        if await self.block_repo.find_by_id((post.author_id, user_id)):
            raise AccessDeniedError
        return await self.post_to_object(post)

    async def new_post(self, user_id: int, request: PostRequest) -> Post:
        """
        Creates a new post
        :param user_id: author ID
        :param request: post info (image and caption)
        :return: the post object
        """
        db_post = await self.post_repo.save(PostModel(author_id=user_id, caption=request.caption))

        img = upload2post(request.image)
        post, _ = await asyncio.gather(
            self.post_to_object(db_post, cached_img=img, new_post=True),
            self.storage_service.store_post(db_post.post_id, img)
        )
        return post

    async def delete_post(self, user_id: int, post_id: int) -> None:
        """
        Deletes a post
        :param user_id: author ID
        :param post_id: post ID
        """
        if db_post := await self.post_repo.find_by_post_id_and_author_id(post_id, user_id):
            await asyncio.gather(
                self.post_repo.delete(db_post),
                self.storage_service.delete_post(post_id)
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
        user = await self.user_repo.find_by_id(user_id)
        assert user is not None, 'Bad authenticated user ID injected'
        return await self.post_repo.find_feed(user_id, limit, limit * page)

    async def like_post(self, user_id: int, post_id: int) -> None:
        """
        Likes a post
        :param user_id: user ID
        :param post_id: post ID
        """
        if not await self.post_repo.find_by_id(post_id):
            raise PostNotFoundError
        await self.like_repo.save(PostLikeRelationship(user_id=user_id, post_id=post_id))

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
        return await self.like_repo.exists_by_post_id_and_user_id(post_id, user_id)
