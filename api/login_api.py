from fastapi import APIRouter, Depends, Path, status

from providers.rate_limiting import auth_limiter
from providers.services import get_auth_service
from security.bearer_auth import get_user
from model import UserCredentials
from service import AuthService

login_router = APIRouter(prefix='/session', tags=['Login'], dependencies=[Depends(auth_limiter)])


@login_router.post('/')
async def login(request: UserCredentials, auth_service: AuthService = Depends(get_auth_service)) -> str:
    """
    Logs in the user
    :param request: login request
    :param auth_service: auth service
    :return: the session token on successful login
    """
    return await auth_service.login(request.username, request.password)


@login_router.delete('/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
async def logout_session(
        user_id: int = Depends(get_user),
        session_id: str = Path(..., min_length=43, max_length=43, pattern=r'^[A-Za-z0-9_-]+$'),
        auth_service: AuthService = Depends(get_auth_service)
) -> None:
    """
    Revokes the session token
    :param user_id: authenticated user ID
    :param session_id: session token to be revoked
    :param auth_service: auth service
    """
    await auth_service.revoke_session(user_id, session_id)
