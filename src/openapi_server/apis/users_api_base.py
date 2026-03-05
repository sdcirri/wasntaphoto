# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.account import Account
from openapi_server.security_api import get_token_bearerAuth

class BaseUsersApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseUsersApi.subclasses = BaseUsersApi.subclasses + (cls,)
    async def search_users(
        self,
        q: Annotated[str, Field(min_length=3, strict=True, max_length=255, description="Your search query")],
    ) -> List[int]:
        """Search registered users on the website"""
        ...


    async def get_user_profile(
        self,
        userID: Annotated[int, Field(strict=True, ge=0)],
    ) -> Account:
        """Returns information about a user (follower count, following count, profile picture (B64-encoded!) and posts) You need to be logged in (provide a valid auth token) in order to view posts. Otherwise, the &#39;posts&#39; property will be empty"""
        ...


    async def get_my_profile(
        self,
    ) -> Account:
        """Returns information about the current user (follower count, following count, profile picture (B64-encoded!) and posts) You need to be logged in (provide a valid auth token) in order to view posts. Otherwise, the &#39;posts&#39; property will be empty"""
        ...
