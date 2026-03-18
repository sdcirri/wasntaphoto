from fastapi import APIRouter, Path, Body, Depends, status

from providers.services import get_comment_service
from security.bearer_auth import get_user
from service import CommentService
from model import Comment


comment_router = APIRouter(prefix='/{post_id}/comments', tags=['Comments'])


@comment_router.post('/')
async def comment_post(
        content: str = Body(..., min_length=1, max_length=2048),
        post_id: int = Path(..., ge=0),
        comment_service: CommentService = Depends(get_comment_service),
        user_id: int = Depends(get_user)
) -> Comment:
    """
    Comment on a post
    :param content: the comment text
    :param post_id: post ID of the post to comment
    :param comment_service: comment service
    :param user_id: authenticated user ID
    :return: the newly created comment
    """
    return await comment_service.create_comment(user_id, post_id, content)


@comment_router.get('/{comment_id}')
async def get_comment(
        comment_id: int = Path(..., ge=0),
        comment_service: CommentService = Depends(get_comment_service),
        _: int = Depends(get_user)
) -> Comment:
    """
    Gets a comment
    :param comment_id: comment ID
    :param comment_service: comment service
    :param _: authenticated user ID (unused)
    :return: the comment info
    """
    return await comment_service.get_comment(comment_id)


@comment_router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: int = Path(..., ge=0),
        comment_service: CommentService = Depends(get_comment_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Deletes a comment
    :param comment_id: comment ID
    :param comment_service: comment service
    :param user_id: authenticated user ID
    """
    await comment_service.delete_comment(user_id, comment_id)


@comment_router.get('/{comment_id}/like')
async def is_liked(
        comment_id: int = Path(..., ge=0),
        comment_service: CommentService = Depends(get_comment_service),
        user_id: int = Depends(get_user)
) -> bool:
    """
    Gets whether the comment was liked by the current user
    :param comment_id: comment ID
    :param comment_service: comment service
    :param user_id: authenticated user ID
    :return: whether the comment was liked by the current user
    """
    return await comment_service.is_comment_liked(user_id, comment_id)


@comment_router.put('/{comment_id}/like', status_code=status.HTTP_204_NO_CONTENT)
async def like_comment(
        comment_id: int = Path(..., ge=0),
        comment_service: CommentService = Depends(get_comment_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Likes a comment
    :param comment_id: comment ID
    :param comment_service: comment service
    :param user_id: authenticated user ID
    """
    await comment_service.like_comment(user_id, comment_id)


@comment_router.delete('/{comment_id}/like', status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(
        comment_id: int = Path(..., ge=0),
        comment_service: CommentService = Depends(get_comment_service),
        user_id: int = Depends(get_user)
) -> None:
    """
    Unlikes a comment
    :param comment_id: comment ID
    :param comment_service: comment service
    :param user_id: authenticated user ID
    """
    await comment_service.unlike_comment(user_id, comment_id)
