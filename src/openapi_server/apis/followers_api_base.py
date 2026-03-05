# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.security_api import get_token_bearerAuth

class BaseFollowersApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseFollowersApi.subclasses = BaseFollowersApi.subclasses + (cls,)
    async def get_followers(
        self,
    ) -> List[int]:
        """See who is following you"""
        ...


    async def remove_follower(
        self,
        followerID: Annotated[int, Field(strict=True, ge=0, description="Follower to remove")],
    ) -> None:
        """Removes a follower from your followers&#39; list"""
        ...


    async def get_blocked(
        self,
    ) -> List[int]:
        """See who you&#39;ve blocked"""
        ...


    async def ban_user(
        self,
        body: Annotated[int, Field(strict=True, ge=0, description="user ID to block")],
    ) -> int:
        """Blocks annoying user. On success returns the blocked user&#39;s ID. Also removes the user from your followers"""
        ...


    async def unban_user(
        self,
        blockedID: Annotated[int, Field(strict=True, ge=0, description="User to unblock")],
    ) -> None:
        """unblocks a previously blocked user"""
        ...


    async def get_following(
        self,
    ) -> List[int]:
        """See who you&#39;re following"""
        ...


    async def follow_user(
        self,
        body: Annotated[int, Field(strict=True, ge=0, description="user ID to follow")],
    ) -> int:
        """Follows a user. On success returns the followed user&#39;s ID"""
        ...


    async def unfollow_user(
        self,
        followingID: Annotated[int, Field(strict=True, ge=0, description="User to unfollow")],
    ) -> None:
        """Unfollows a user"""
        ...
