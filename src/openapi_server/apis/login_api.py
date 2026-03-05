# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.login_api_base import BaseLoginApi
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
from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated
from openapi_server.models.registration_request import RegistrationRequest
from openapi_server.models.user_credentials import UserCredentials
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/session",
    responses={
        200: {"model": str, "description": "User log-in action successful"},
        403: {"description": "Access denied"},
    },
    tags=["Login"],
    summary="Logs in the user",
    response_model_by_alias=True,
)
async def do_login(
    user_credentials: Annotated[UserCredentials, Field(description="User details")] = Body(None, description="User details"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> str:
    """Attempts to login, if successul the user token is returned."""
    if not BaseLoginApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLoginApi.subclasses[0]().do_login(user_credentials)


@router.post(
    "/users",
    responses={
        200: {"model": str, "description": "Registration successful"},
        400: {"description": "Weak password"},
        409: {"description": "Username already taken"},
    },
    tags=["Login"],
    summary="Register to the website",
    response_model_by_alias=True,
)
async def register(
    registration_request: Annotated[RegistrationRequest, Field(description="Registration data")] = Body(None, description="Registration data"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> str:
    """Registers a new user and issues an access token after successful registration"""
    if not BaseLoginApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLoginApi.subclasses[0]().register(registration_request)
