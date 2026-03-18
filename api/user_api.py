from fastapi import APIRouter, Depends, Query, Request, Path, Body, status, HTTPException

from providers.services import get_auth_service, get_user_service
from model import RegistrationRequest, UserAccount
from service import AuthService, UserService
from security.bearer_auth import get_user

from .post_api import post_router


user_router = APIRouter(prefix='/users', tags=['Users'])
user_router.include_router(post_router)


def target_user_id(request: Request, me_id: int = Depends(get_user)) -> int:
    raw = request.path_params.get('user_id')
    if raw in (None, 'me'):
        return me_id
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise HTTPException(status_code=422)


@user_router.get('/')
async def search_users(
        user_service: UserService = Depends(get_user_service),
        q: str = Query(..., min_length=3, max_length=40),
        l: int = Query(10, alias='limit', ge=1, le=100)
) -> list[int]:
    """
    Search for users
    :param user_service: user service
    :param q: query string
    :param l: number of results to return (max 100, default 10)
    :return: the list of the first *l* matching user IDs
    """
    return await user_service.search_users(q, l)


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
        user_service: UserService = Depends(get_user_service),
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
async def get_user_account(
        target_uid: int = Depends(target_user_id),
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> UserAccount:
    """
    Gets the specified user account info
    :param user_service: user service
    :param target_uid: target user ID (can also be 'me')
    :param user_id: authenticated user ID
    :return: the current user account info, if it exists
    """
    return await user_service.get_user(target_uid, user_id)


@user_router.put('/me/username', status_code=status.HTTP_204_NO_CONTENT)
async def update_username(
        username: str = Body(..., min_length=3, max_length=40),
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


@user_router.put('/me/pp', status_code=status.HTTP_204_NO_CONTENT)
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


@user_router.delete('/me/followers/{to_remove_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_follower(
        to_remove_id: int = Path(..., ge=0),
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Removes a follower
    :param to_remove_id: user ID of the follower to remove
    :param user_service: user service
    :param user_id: authenticated user ID
    """
    await user_service.remove_follower(user_id, to_remove_id)


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


@user_router.post('/me/following/{to_follow_id}')
async def follow_user(
        to_follow_id: int = Path(..., ge=0),
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Follows a user
    :param to_follow_id: user ID of the user to follow
    :param user_service: user service
    :param user_id: authenticated user ID
    """
    await user_service.follow(user_id, to_follow_id)


@user_router.delete('/me/following/{to_unfollow_id}', status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
        to_unfollow_id: int = Path(..., ge=0),
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Unfollows a user
    :param to_unfollow_id: user ID of the user to unfollow
    :param user_service: user service
    :param user_id: authenticated user ID
    """
    await user_service.unfollow(user_id, to_unfollow_id)


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


@user_router.post('/me/blocked/{to_block_id}')
async def block_user(
        to_block_id: int = Path(..., ge=0),
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Blocks a user
    :param to_block_id: user ID of the user to block
    :param user_service: user service
    :param user_id: authenticated user ID
    """
    await user_service.block_user(user_id, to_block_id)


@user_router.delete('/me/blocked/{to_unblock_id}', status_code=status.HTTP_204_NO_CONTENT)
async def unblock_user(
        to_unblock_id: int = Path(..., ge=0),
        user_service: UserService = Depends(get_user_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Unblocks a user
    :param to_unblock_id: user ID of the user to block
    :param user_service: user service
    :param user_id: authenticated user ID
    """
    await user_service.unblock_user(user_id, to_unblock_id)
