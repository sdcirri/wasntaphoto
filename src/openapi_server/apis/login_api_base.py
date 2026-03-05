# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated
from openapi_server.models.registration_request import RegistrationRequest
from openapi_server.models.user_credentials import UserCredentials
from openapi_server.security_api import get_token_bearerAuth

class BaseLoginApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseLoginApi.subclasses = BaseLoginApi.subclasses + (cls,)
    async def do_login(
        self,
        user_credentials: Annotated[UserCredentials, Field(description="User details")],
    ) -> str:
        """Attempts to login, if successul the user token is returned."""
        ...


    async def register(
        self,
        registration_request: Annotated[RegistrationRequest, Field(description="Registration data")],
    ) -> str:
        """Registers a new user and issues an access token after successful registration"""
        ...
