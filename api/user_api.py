from fastapi import APIRouter, Depends, Query, Request, Path, Body

from providers.services import get_auth_service, get_user_service, get_post_service
from model import RegistrationRequest, UserAccount, Post, PostRequest
from service import AuthService, UserService, PostService
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
        user_id: int = Path(..., ge=0),
        user_service: UserService = Depends(get_user_service)
) -> UserAccount:
    """
    Gets the specified user account info
    :param user_service: user service
    :param user_id: user ID
    :return: the current user account info, if it exists
    """
    return await user_service.get_user(user_id)


@user_router.get('/{user_id}/posts/{post_id}')
async def get_post(
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        _: int = Depends(get_user)
) -> Post:
    """
    Get a post
    :param post_id: post ID
    :param post_service: post service
    :param _: authenticated user ID (unused)
    :return: the requested post
    """
    return await post_service.get_post(post_id)


@user_router.get('/{user_id}/posts/{post_id}/like')
async def is_liked(
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> bool:
    """
    Gets whether the post was liked by the current user
    :param post_id: post ID
    :param post_service: post service
    :param user_id: authenticated user ID
    :return: the requested post
    """
    return await post_service.is_liked(user_id, post_id)


@user_router.put('/{user_id}/posts/{post_id}/like')
async def like_post(
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Likes a post
    :param post_id: post ID
    :param post_service: post service
    :param user_id: authenticated user ID
    """
    await post_service.like_post(user_id, post_id)


@user_router.delete('/{user_id}/posts/{post_id}/like')
async def unlike_post(
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Unlikes a post
    :param post_id: post ID
    :param post_service: post service
    :param user_id: authenticated user ID
    """
    await post_service.unlike_post(user_id, post_id)


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


@user_router.delete('/me/followers/{to_remove_id}')
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


@user_router.delete('/me/following/{to_unfollow_id}')
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


@user_router.delete('/me/blocked/{to_unblock_id}')
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


@user_router.post('/me/posts')
async def new_post(
        request: PostRequest,
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> Post:
    """
    Get a post
    :param request: post creation request
    :param post_service: post service
    :param user_id: authenticated user ID
    :return: the requested post
    """
    return await post_service.new_post(user_id, request)


@user_router.get('/me/posts/{post_id}')
async def get_post(
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        _: int = Depends(get_user)
) -> Post:
    """
    Get a post
    :param post_id: post ID
    :param post_service: post service
    :param _: authenticated user ID (unused)
    :return: the requested post
    """
    return await post_service.get_post(post_id)


@user_router.get('/me/posts/{post_id}/likes')
async def get_likes(
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> list[int]:
    """
    Get your posts likes
    :param post_id: post ID
    :param post_service: post service
    :param user_id: authenticated user ID
    :return: list of users who liked the post
    """
    return await post_service.get_post_likes(user_id, post_id)


@user_router.delete('/me/posts/{post_id}')
async def delete_post(
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Deletes a post
    :param post_id: post ID
    :param post_service: post service
    :param user_id: authenticated user ID
    """
    await post_service.delete_post(post_id, user_id)
