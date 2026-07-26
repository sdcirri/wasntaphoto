from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, Depends

from providers.services import get_auth_service
from exceptions import BadAuthError
from service import AuthService


SESSION_COOKIE_NAME = 'WASASESSIONID'

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user(
        request: Request,
        creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        auth_service: AuthService = Depends(get_auth_service)
) -> int:
    """
    Resolves the bearer auth token to the corresponding user ID
    :param request: incoming request
    :param creds: HTTPBearer credentials
    :param auth_service: auth service
    :return: the user ID, if the auth token is valid
    """
    token = creds.credentials if creds else request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise BadAuthError
    return await auth_service.resolve_token(token)
