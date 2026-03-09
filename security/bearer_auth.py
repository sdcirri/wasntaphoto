from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.params import Depends

from providers.services import get_auth_service
from service import AuthService


bearer_scheme = HTTPBearer(auto_error=True)


async def get_user(
        creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        auth_service: AuthService = Depends(get_auth_service)
) -> int:
    """
    Resolves the bearer auth token to the corresponding user ID
    :param creds: HTTPBearer credentials
    :param auth_service: auth service
    :return: the user ID, if the auth token is valid
    """
    return await auth_service.resolve_token(creds.credentials)
