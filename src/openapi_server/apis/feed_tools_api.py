# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.feed_tools_api_base import BaseFeedToolsApi
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
from pydantic import Field, StrictBool, StrictInt, field_validator
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.comment import Comment
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/feed",
    responses={
        200: {"model": List[int], "description": "Operation successful"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Trying to view somebody else&#39;s feed"},
    },
    tags=["Feed tools"],
    summary="Retrieve feed",
    response_model_by_alias=True,
)
async def get_my_stream(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """Retrieves your feed made of the posts of the accounts you follow in reverse chronological order"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().get_my_stream()


@router.get(
    "/users/{userID}/posts/{postID}/like",
    responses={
        200: {"model": bool, "description": "Operation successful"},
        401: {"description": "Unauthenticated or bad authentication"},
        404: {"description": "Post not found"},
    },
    tags=["Feed tools"],
    summary="Get liked",
    response_model_by_alias=True,
)
async def is_liked(
    userID: Annotated[int, Field(strict=True, ge=0, description="author ID")] = Path(..., description="author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")] = Path(..., description="Post ID", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> bool:
    """Checks whether the post has been liked by current user"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().is_liked(userID, postID)


@router.put(
    "/users/{userID}/posts/{postID}/like",
    responses={
        201: {"model": int, "description": "Operation successful"},
        400: {"description": "Bad auth token or bad post ID"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden: user blocked you!"},
        404: {"description": "Post not found"},
    },
    tags=["Feed tools"],
    summary="Like a post",
    response_model_by_alias=True,
)
async def like_photo(
    userID: Annotated[int, Field(strict=True, ge=0, description="author ID")] = Path(..., description="author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0)] = Path(..., description="", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Adds a like as the logged user. On success returns the new like count"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().like_photo(userID, postID)


@router.delete(
    "/users/{userID}/posts/{postID}/like",
    responses={
        200: {"model": int, "description": "Operation successful"},
        400: {"description": "Bad auth token, bad post ID or post wasn&#39;t liked"},
        401: {"description": "Unauthenticated"},
        404: {"description": "Post not found"},
    },
    tags=["Feed tools"],
    summary="Unlikes a post",
    response_model_by_alias=True,
)
async def unlike_photo(
    userID: Annotated[int, Field(strict=True, ge=0, description="author ID")] = Path(..., description="author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0)] = Path(..., description="", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Removes the like as the logged user (if any). On success returns the new like count"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().unlike_photo(userID, postID)


@router.post(
    "/users/{userID}/posts/{postID}/comments",
    responses={
        201: {"model": int, "description": "Operation successful"},
        400: {"description": "Empty comment or comment too long"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Cannot comment no post: poster blocked you!"},
        404: {"description": "Post not found"},
    },
    tags=["Feed tools"],
    summary="Comment on a post",
    response_model_by_alias=True,
)
async def comment_photo(
    userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")] = Path(..., description="post author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")] = Path(..., description="Post ID", ge=0),
    body: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=2048)]] = Body(None, description="", regex=r"^.*?$", min_length=0, max_length=2048),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Comments on a post. On success returns the new comment ID"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().comment_photo(userID, postID, body)


@router.get(
    "/users/{userID}/posts/{postID}/comments/{commentID}",
    responses={
        200: {"model": Comment, "description": "Operation successful"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden: author blocked you!"},
        404: {"description": "Comment not found"},
    },
    tags=["Feed tools"],
    summary="Get comment",
    response_model_by_alias=True,
)
async def get_comment(
    userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")] = Path(..., description="post author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")] = Path(..., description="Post ID", ge=0),
    commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")] = Path(..., description="Comment ID", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Comment:
    """Retrieves the comment associated with the supplied ID"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().get_comment(userID, postID, commentID)


@router.delete(
    "/users/{userID}/posts/{postID}/comments/{commentID}",
    responses={
        204: {"description": "Successful operation"},
        400: {"description": "Bad comment ID"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden, you cannot delete somebody else&#39;s comment!"},
        404: {"description": "Comment not found"},
    },
    tags=["Feed tools"],
    summary="Remove a comment",
    response_model_by_alias=True,
)
async def uncomment_photo(
    userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")] = Path(..., description="post author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")] = Path(..., description="Post ID", ge=0),
    commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")] = Path(..., description="Comment ID", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Removes the specified comment. Only the author can do that!"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().uncomment_photo(userID, postID, commentID)


@router.get(
    "/users/{userID}/posts/{postID}/comments/{commentID}/like",
    responses={
        200: {"model": bool, "description": "Operation successful"},
        401: {"description": "Unauthenticated or bad authentication"},
        404: {"description": "Post not found"},
    },
    tags=["Feed tools"],
    summary="Is comment liked?",
    response_model_by_alias=True,
)
async def is_comment_liked(
    userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")] = Path(..., description="post author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")] = Path(..., description="Post ID", ge=0),
    commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")] = Path(..., description="Comment ID", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> bool:
    """Checks whether the comment has been liked by you"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().is_comment_liked(userID, postID, commentID)


@router.put(
    "/users/{userID}/posts/{postID}/comments/{commentID}/like",
    responses={
        201: {"model": int, "description": "Operation successful"},
        400: {"description": "Bad authentication token or bad comment ID"},
        401: {"description": "Unauthenticated"},
        403: {"description": "Cannot like: author blocked you!"},
        404: {"description": "Comment not found"},
    },
    tags=["Feed tools"],
    summary="Likes a comment",
    response_model_by_alias=True,
)
async def like_comment(
    userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")] = Path(..., description="post author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")] = Path(..., description="Post ID", ge=0),
    commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")] = Path(..., description="Comment ID", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Adds a like to a comment as the logged user. On success returns the new like count"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().like_comment(userID, postID, commentID)


@router.delete(
    "/users/{userID}/posts/{postID}/comments/{commentID}/like",
    responses={
        200: {"model": int, "description": "Operation successful"},
        400: {"description": "Bad authentication token, userID or comment ID"},
        401: {"description": "Unauthenticated"},
        404: {"description": "Comment not found or comment wasn&#39;t liked"},
    },
    tags=["Feed tools"],
    summary="Unlike a comment",
    response_model_by_alias=True,
)
async def unlike_comment(
    userID: Annotated[int, Field(strict=True, ge=0, description="post author ID")] = Path(..., description="post author ID", ge=0),
    postID: Annotated[int, Field(strict=True, ge=0, description="Post ID")] = Path(..., description="Post ID", ge=0),
    commentID: Annotated[int, Field(strict=True, ge=0, description="Comment ID")] = Path(..., description="Comment ID", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> int:
    """Removes the like from a comment as the logged user (if any). On success returns the new like count"""
    if not BaseFeedToolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseFeedToolsApi.subclasses[0]().unlike_comment(userID, postID, commentID)
