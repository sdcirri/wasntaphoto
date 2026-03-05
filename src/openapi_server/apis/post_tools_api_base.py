# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.post import Post
from openapi_server.models.post_params import PostParams
from openapi_server.security_api import get_token_bearerAuth

class BasePostToolsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePostToolsApi.subclasses = BasePostToolsApi.subclasses + (cls,)
    async def get_my_posts(
        self,
    ) -> List[int]:
        """Get your posts"""
        ...


    async def upload_photo(
        self,
        post_params: Optional[PostParams],
    ) -> int:
        """Creates a new post with the supplied image and, optionally, a description. On success returns the post ID"""
        ...


    async def get_my_post(
        self,
        postID: Annotated[int, Field(strict=True, ge=0)],
    ) -> Post:
        """Get information on your post"""
        ...


    async def delete_photo(
        self,
        postID: Annotated[int, Field(strict=True, ge=0)],
    ) -> None:
        """Deletes one of your posts. Be careful! Once deleted, posts are lost forever!"""
        ...


    async def get_likes(
        self,
        postID: Annotated[int, Field(strict=True, ge=0)],
    ) -> List[int]:
        """Get likes on YOUR post. Nobody but the author can see who liked a post"""
        ...


    async def get_user_posts(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="user ID")],
    ) -> List[int]:
        """Get a user&#39;s posts"""
        ...


    async def get_post(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="author ID")],
        postID: Annotated[int, Field(strict=True, ge=0)],
    ) -> Post:
        """Get information on one post"""
        ...
