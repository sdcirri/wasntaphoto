# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.post_tools_api_base import BasePostToolsApi
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
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.post import Post
from openapi_server.models.post_params import PostParams
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/users/me/posts",
    responses={
        200: {"model": List[int], "description": "Successful operation"},
        400: {"description": "Bad auth token or userID, malformed post object, image too big or caption too long"},
        401: {"description": "Unauthenticated"},
    },
    tags=["Post tools"],
    summary="User posts",
    response_model_by_alias=True,
)
async def get_my_posts(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """Get your posts"""
    if not BasePostToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostToolsApi.subclasses[0]().get_my_posts()


@router.post(
    "/users/me/posts",
    responses={
        201: {"model": int, "description": "Successful operation"},
        400: {"description": "Malformed post object, image too big or caption too long"},
        401: {"description": "Unauthenticated"},
    },
    tags=["Post tools"],
    summary="New post",
    response_model_by_alias=True,
)
async def upload_photo(
    post_params: Optional[PostParams] = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Creates a new post with the supplied image and, optionally, a description. On success returns the post ID"""
    if not BasePostToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostToolsApi.subclasses[0]().upload_photo(post_params)


@router.get(
    "/users/me/posts/{postID}",
    responses={
        200: {"model": Post, "description": "Operation successful"},
        401: {"description": "Unauthenticated or bad auth token"},
        403: {"description": "User blocked you!"},
        404: {"description": "Post not found"},
    },
    tags=["Post tools"],
    summary="Post info",
    response_model_by_alias=True,
)
async def get_my_post(
    postID: Annotated[int, Field(strict=True, ge=0)] = Path(..., description="", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Post:
    """Get information on your post"""
    if not BasePostToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostToolsApi.subclasses[0]().get_my_post(postID)


@router.delete(
    "/users/me/posts/{postID}",
    responses={
        204: {"description": "Operation successful"},
        401: {"description": "Unauthenticated"},
        404: {"description": "Post not found"},
    },
    tags=["Post tools"],
    summary="Delete post",
    response_model_by_alias=True,
)
async def delete_photo(
    postID: Annotated[int, Field(strict=True, ge=0)] = Path(..., description="", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Deletes one of your posts. Be careful! Once deleted, posts are lost forever!"""
    if not BasePostToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostToolsApi.subclasses[0]().delete_photo(postID)


@router.get(
    "/users/me/posts/{postID}/likes",
    responses={
        200: {"model": List[int], "description": "Operation successful"},
        400: {"description": "Bad auth token"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden"},
        404: {"description": "Post not found"},
    },
    tags=["Post tools"],
    summary="Get likes",
    response_model_by_alias=True,
)
async def get_likes(
    postID: Annotated[int, Field(strict=True, ge=0)] = Path(..., description="", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """Get likes on YOUR post. Nobody but the author can see who liked a post"""
    if not BasePostToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostToolsApi.subclasses[0]().get_likes(postID)


@router.get(
    "/users/{userID}/posts",
    responses={
        200: {"model": List[int], "description": "Successful operation"},
        400: {"description": "Bad auth token or userID, malformed post object, image too big or caption too long"},
        401: {"description": "Unauthenticated"},
    },
    tags=["Post tools"],
    summary="User posts",
    response_model_by_alias=True,
)
async def get_user_posts(
    userID: Annotated[int, Field(strict=True, ge=0, description="user ID")] = Path(..., description="user ID", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """Get a user&#39;s posts"""
    if not BasePostToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostToolsApi.subclasses[0]().get_user_posts(userID)


@router.get(
    "/users/{userID}/posts/{postID}",
    responses={
        200: {"model": Post, "description": "Operation successful"},
        401: {"description": "Unauthenticated or bad auth token"},
        403: {"description": "User blocked you!"},
        404: {"description": "Post not found"},
    },
    tags=["Post tools"],
    summary="Post info",
    response_model_by_alias=True,
)
async def get_post(
    userID: Annotated[int, Field(strict=True, ge=0, description="author ID")] = Path(..., description="author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0)] = Path(..., description="", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Post:
    """Get information on one post"""
    if not BasePostToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostToolsApi.subclasses[0]().get_post(userID, postID)
