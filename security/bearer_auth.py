from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, Response, Depends

from providers.services import get_auth_service
from exceptions import BadAuthError
from service import AuthService


SESSION_COOKIE_NAME = 'WASASESSIONID'

bearer_scheme = HTTPBearer(auto_error=False)


def get_session_id(
        request: Request,
        creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
) -> str:
    """
    Resolve the session ID from a request, raises on no auth
    :param request: incoming request
    :param creds: HTTP Bearer credentials
    :return: the session ID, if provided
    """
    token = creds.credentials if creds else request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise BadAuthError
    return token


async def get_user(
        session_id: str = Depends(get_session_id),
        auth_service: AuthService = Depends(get_auth_service)
) -> int:
    """
    Resolves the bearer auth token to the corresponding user ID
    :param session_id: resolved session ID
    :param auth_service: auth service
    :return: the user ID, if the auth token is valid
    """
    return await auth_service.resolve_token(session_id)


def set_session_cookie(response: Response, token: str) -> None:
    """
    Sets the session cookie
    :param response: outgoing response
    :param token: token to set
    """
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        # Should be True in prod, since this is a demo
        # project it should be False to work in local
        secure=False,
        samesite='lax',
        max_age=AuthService.SESSION_MAX_AGE
    )
