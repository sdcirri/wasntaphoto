# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.account_management_api_base import BaseAccountManagementApi
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
from pydantic import Field, StrictBytes, StrictStr, field_validator
from typing import Any, Optional, Tuple, Union
from typing_extensions import Annotated
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.put(
    "/users/me/username",
    responses={
        200: {"model": str, "description": "Operation successful"},
        400: {"description": "Username already taken"},
        401: {"description": "Unauthenticated"},
    },
    tags=["Account management"],
    summary="Sets the username",
    response_model_by_alias=True,
)
async def set_my_user_name(
    body: Annotated[str, Field(min_length=3, strict=True, max_length=40, description="Username to set")] = Body(None, description="Username to set", regex=r"ˆ.*?$", min_length=3, max_length=40),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> str:
    """Changes the logged in user&#39;s username. Returns the same username on success"""
    if not BaseAccountManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAccountManagementApi.subclasses[0]().set_my_user_name(body)


@router.put(
    "/users/me/pp",
    responses={
        204: {"description": "Operation successful"},
        400: {"description": "Bad image"},
        401: {"description": "Unauthenticated"},
    },
    tags=["Account management"],
    summary="Set a profile picture",
    response_model_by_alias=True,
)
async def set_pro_pic(
    body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Sets the profile picture for the logged in user, the picture should be provided in the request body."""
    if not BaseAccountManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAccountManagementApi.subclasses[0]().set_pro_pic(body)
