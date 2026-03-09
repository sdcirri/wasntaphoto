from fastapi import APIRouter, Depends, Query, Request

from providers.services import get_auth_service, get_user_service
from model import RegistrationRequest, UserAccount
from service import AuthService, UserService
from security.bearer_auth import get_user


user_router = APIRouter(prefix='/users', tags=['Users'])


@user_router.post('/')
async def register_user(request: RegistrationRequest, auth_service: AuthService = Depends(get_auth_service)) -> str:
    """
    Registers in the user
    :param request: registration request
    :param auth_service: auth service
    :return: the session token on successful registration
    """
    return await auth_service.register(request.username, request.password)


@user_router.get('/')
async def search_users(
        user_service: UserService = Depends(get_auth_service),
        q: str = Query(None, alias='q', min_length=3, max_length=40),
        limit: int = Query(10, alias='limit', ge=1, le=100)
) -> list[int]:
    """
    Run a text search on users
    :param user_service: user service
    :param q: search query
    :param limit: number of results to return (max 100, default 10)
    :return: the list of the first matching user IDs
    """
    return await user_service.search_users(q, limit)


@user_router.get('/{user_id}')
async def get_user(
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> UserAccount:
    """
    Gets the specified user account info
    :param user_service: user service
    :param user_id: user ID
    :return: the current user account info, if it exists
    """
    return await user_service.get_user(user_id)


@user_router.get('/me')
async def get_current_user(
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> UserAccount:
    """
    Gets the current user account info
    :param user_service: user service
    :param user_id: authenticated user ID
    :return: the current user account info
    """
    return await user_service.get_user(user_id)


@user_router.put('/me/username')
async def update_username(
        username: str,
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Updates the current user username
    :param username: new username to set
    :param user_service: user service
    :param user_id: authenticated user ID
    """
    await user_service.set_username(user_id, username)


@user_router.put('/me/pp')
async def update_propic(
        request: Request,
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Updates the current user propic
    :param request: new propic (raw bytes)
    :param user_service: user service
    :param user_id: authenticated user ID
    """
    image = await request.body()
    await user_service.set_propic(user_id, image)


@user_router.get('/me/followers')
async def get_followers(
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> list[int]:
    """
    Get the current user followers
    :param user_service: user service
    :param user_id: authenticated user ID
    :return: the current user followers
    """
    return await user_service.get_followers(user_id)


@user_router.get('/me/following')
async def get_following(
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> list[int]:
    """
    Get the current user followed accounts
    :param user_service: user service
    :param user_id: authenticated user ID
    :return: the current user followed accounts
    """
    return await user_service.get_following(user_id)


@user_router.get('/me/blocked')
async def get_blocked(
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> list[int]:
    """
    Get the current user blocked accounts
    :param user_service: user service
    :param user_id: authenticated user ID
    :return: the current user blocked accounts
    """
    return await user_service.get_blocked(user_id)
