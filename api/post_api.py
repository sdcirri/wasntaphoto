from fastapi import Request, Depends, APIRouter, Path, HTTPException

from providers.services import get_post_service
from security.bearer_auth import get_user
from model import Post, PostRequest
from service import PostService

from .comment_api import comment_router


post_router = APIRouter(prefix='/{author_id}/posts', tags=['Posts'])
post_router.include_router(comment_router)


def target_user_id(request: Request, me_id: int = Depends(get_user)) -> int:
    raw = request.path_params.get('author_id')
    if raw in (None, "me"):
        return me_id
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise HTTPException(status_code=422)


@post_router.get('/{post_id}')
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


@post_router.get('/{post_id}/like')
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


@post_router.put('/{post_id}/like')
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


@post_router.delete('/{post_id}/like')
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


@post_router.post('/')
async def new_post(
        request: PostRequest,
        target_id: int = Depends(target_user_id),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> Post:
    """
    Get a post
    :param request: post creation request
    :param target_id: user ID (must be "me")
    :param post_service: post service
    :param user_id: authenticated user ID
    :return: the requested post
    """
    if target_id != user_id:
        raise HTTPException(status_code=400)
    return await post_service.new_post(user_id, request)


@post_router.get('/{post_id}/likes')
async def get_likes(
        target_id: int = Depends(target_user_id),
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> list[int]:
    """
    Get your posts likes
    :param target_id: user ID (must be "me")
    :param post_id: post ID
    :param post_service: post service
    :param user_id: authenticated user ID
    :return: list of users who liked the post
    """
    if target_id != user_id:
        raise HTTPException(status_code=400)
    return await post_service.get_post_likes(user_id, post_id)


@post_router.delete('/{post_id}')
async def delete_post(
        target_id: int = Depends(target_user_id),
        post_id: int = Path(..., ge=0),
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Deletes a post
    :param target_id: user ID (must be "me")
    :param post_id: post ID
    :param post_service: post service
    :param user_id: authenticated user ID
    """
    if target_id != user_id:
        raise HTTPException(status_code=400)
    await post_service.delete_post(user_id, post_id)
