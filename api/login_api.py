from fastapi import APIRouter, Depends

from providers.services import get_auth_service
from model import UserCredentials
from service import AuthService


login_router = APIRouter(prefix='/session', tags=['Login'])


@login_router.post('/')
async def login(request: UserCredentials, auth_service: AuthService = Depends(get_auth_service)) -> str:
    """
    Logs in the user
    :param request: login request
    :param auth_service: auth service
    :return: the session token on successful login
    """
    return await auth_service.login(request.username, request.password)
