# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.followers_api_base import BaseFollowersApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/users/me/followers",
    responses={
        200: {"model": List[int], "description": "successful operation"},
        400: {"description": "Bad auth token"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden: cannot view somebody else&#39;s followers"},
    },
    tags=["Followers"],
    summary="List followers",
    response_model_by_alias=True,
)
async def get_followers(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """See who is following you"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().get_followers()


@router.delete(
    "/users/me/followers/{followerID}",
    responses={
        204: {"description": "Successful operation"},
        400: {"description": "Bad auth token or trying to remove yourself"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Trying to edit somebody else&#39;s followers"},
        404: {"description": "User not found or not following"},
    },
    tags=["Followers"],
    summary="Remove follower",
    response_model_by_alias=True,
)
async def remove_follower(
    followerID: Annotated[int, Field(strict=True, ge=0, description="Follower to remove")] = Path(..., description="Follower to remove", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Removes a follower from your followers&#39; list"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().remove_follower(followerID)


@router.get(
    "/users/me/blocked",
    responses={
        200: {"model": List[int], "description": "Successful operation"},
        400: {"description": "Bad auth token"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden: cannot view somebody else&#39;s blocks"},
    },
    tags=["Followers"],
    summary="List blocked",
    response_model_by_alias=True,
)
async def get_blocked(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """See who you&#39;ve blocked"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().get_blocked()


@router.post(
    "/users/me/blocked",
    responses={
        200: {"model": int, "description": "Successful operation"},
        400: {"description": "Bad auth token, bad userID, already blocked or trying to block yourself"},
        401: {"description": "Unauthenticated"},
        404: {"description": "User not found"},
    },
    tags=["Followers"],
    summary="Block user",
    response_model_by_alias=True,
)
async def ban_user(
    body: Annotated[int, Field(strict=True, ge=0, description="user ID to block")] = Body(None, description="user ID to block", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Blocks annoying user. On success returns the blocked user&#39;s ID. Also removes the user from your followers"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().ban_user(body)


@router.delete(
    "/users/me/blocked/{blockedID}",
    responses={
        204: {"description": "Successful operation"},
        400: {"description": "Bad auth token, bad userID or trying to unblock yourself"},
        401: {"description": "Unauthenticated"},
        404: {"description": "User not found or not blocked"},
    },
    tags=["Followers"],
    summary="Ublock user",
    response_model_by_alias=True,
)
async def unban_user(
    blockedID: Annotated[int, Field(strict=True, ge=0, description="User to unblock")] = Path(..., description="User to unblock", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """unblocks a previously blocked user"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().unban_user(blockedID)


@router.get(
    "/users/me/following",
    responses={
        200: {"model": List[int], "description": "Successful operation"},
        400: {"description": "Bad auth token"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden: cannot view somebody else&#39;s follows"},
    },
    tags=["Followers"],
    summary="List follows",
    response_model_by_alias=True,
)
async def get_following(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """See who you&#39;re following"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().get_following()


@router.post(
    "/users/me/following",
    responses={
        201: {"model": int, "description": "Successful operation"},
        400: {"description": "bad auth token, bad userID, already following or trying to follow yourself"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden: user blocked you!"},
        404: {"description": "User not found"},
    },
    tags=["Followers"],
    summary="Follow user",
    response_model_by_alias=True,
)
async def follow_user(
    body: Annotated[int, Field(strict=True, ge=0, description="user ID to follow")] = Body(None, description="user ID to follow", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Follows a user. On success returns the followed user&#39;s ID"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().follow_user(body)


@router.delete(
    "/users/me/following/{followingID}",
    responses={
        204: {"description": "Successful operation"},
        400: {"description": "Bad auth token, bad userID or trying to unfollow yourself"},
        401: {"description": "Unauthenticated"},
        404: {"description": "User not found or not following"},
    },
    tags=["Followers"],
    summary="Unfollow user",
    response_model_by_alias=True,
)
async def unfollow_user(
    followingID: Annotated[int, Field(strict=True, ge=0, description="User to unfollow")] = Path(..., description="User to unfollow", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Unfollows a user"""
    if not BaseFollowersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFollowersApi.subclasses[0]().unfollow_user(followingID)
