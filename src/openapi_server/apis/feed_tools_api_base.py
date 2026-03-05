# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictBool, StrictInt, field_validator
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.comment import Comment
from openapi_server.security_api import get_token_bearerAuth

class BaseFeedToolsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseFeedToolsApi.subclasses = BaseFeedToolsApi.subclasses + (cls,)
    async def get_my_stream(
        self,
    ) -> List[int]:
        """Retrieves your feed made of the posts of the accounts you follow in reverse chronological order"""
        ...


    async def is_liked(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="author ID")],
        postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")],
    ) -> bool:
        """Checks whether the post has been liked by current user"""
        ...


    async def like_photo(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="author ID")],
        postID: Annotated[int, Field(strict=True, ge=0)],
    ) -> int:
        """Adds a like as the logged user. On success returns the new like count"""
        ...


    async def unlike_photo(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="author ID")],
        postID: Annotated[int, Field(strict=True, ge=0)],
    ) -> int:
        """Removes the like as the logged user (if any). On success returns the new like count"""
        ...


    async def comment_photo(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")],
        postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")],
        body: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=2048)]],
    ) -> int:
        """Comments on a post. On success returns the new comment ID"""
        ...


    async def get_comment(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")],
        postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")],
        commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")],
    ) -> Comment:
        """Retrieves the comment associated with the supplied ID"""
        ...


    async def uncomment_photo(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")],
        postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")],
        commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")],
    ) -> None:
        """Removes the specified comment. Only the author can do that!"""
        ...


    async def is_comment_liked(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")],
        postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")],
        commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")],
    ) -> bool:
        """Checks whether the comment has been liked by you"""
        ...


    async def like_comment(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")],
        postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")],
        commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")],
    ) -> int:
        """Adds a like to a comment as the logged user. On success returns the new like count"""
        ...


    async def unlike_comment(
        self,
        userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")],
        postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")],
        commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")],
    ) -> int:
        """Removes the like from a comment as the logged user (if any). On success returns the new like count"""
        ...
