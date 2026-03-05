# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.users_api_base import BaseUsersApi
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
from openapi_server.models.account import Account
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/users",
    responses={
        200: {"model": List[int], "description": "Successful operation"},
        400: {"description": "Empty query"},
    },
    tags=["Users"],
    summary="Search for users",
    response_model_by_alias=True,
)
async def search_users(
    q: Annotated[str, Field(min_length=3, strict=True, max_length=255, description="Your search query")] = Query(None, description="Your search query", alias="q", min_length=3, max_length=255),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[int]:
    """Search registered users on the website"""
    if not BaseUsersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsersApi.subclasses[0]().search_users(q)


@router.get(
    "/users/{userID}",
    responses={
        200: {"model": Account, "description": "Operation successful"},
        400: {"description": "Bad auth token or bad userID"},
        403: {"description": "Forbidden: user blocked you!"},
        404: {"description": "User not found"},
    },
    tags=["Users"],
    summary="Profile info",
    response_model_by_alias=True,
)
async def get_user_profile(
    userID: Annotated[int, Field(strict=True, ge=0)] = Path(..., description="", ge=0),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Account:
    """Returns information about a user (follower count, following count, profile picture (B64-encoded!) and posts) You need to be logged in (provide a valid auth token) in order to view posts. Otherwise, the &#39;posts&#39; property will be empty"""
    if not BaseUsersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsersApi.subclasses[0]().get_user_profile(userID)


@router.get(
    "/users/me",
    responses={
        200: {"model": Account, "description": "Operation successful"},
        400: {"description": "Bad auth token"},
    },
    tags=["Users"],
    summary="Profile info",
    response_model_by_alias=True,
)
async def get_my_profile(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Account:
    """Returns information about the current user (follower count, following count, profile picture (B64-encoded!) and posts) You need to be logged in (provide a valid auth token) in order to view posts. Otherwise, the &#39;posts&#39; property will be empty"""
    if not BaseUsersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsersApi.subclasses[0]().get_my_profile()
