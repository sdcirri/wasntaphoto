# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictBytes, StrictStr, field_validator
from typing import Any, Optional, Tuple, Union
from typing_extensions import Annotated
from openapi_server.security_api import get_token_bearerAuth

class BaseAccountManagementApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAccountManagementApi.subclasses = BaseAccountManagementApi.subclasses + (cls,)
    async def set_my_user_name(
        self,
        body: Annotated[str, Field(min_length=3, strict=True, max_length=40, description="Username to set")],
    ) -> str:
        """Changes the logged in user&#39;s username. Returns the same username on success"""
        ...


    async def set_pro_pic(
        self,
        body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]],
    ) -> None:
        """Sets the profile picture for the logged in user, the picture should be provided in the request body."""
        ...
