from fastapi import APIRouter, Depends, Query

from providers.services import get_post_service
from security.bearer_auth import get_user
from service import PostService

feed_router = APIRouter(prefix='/feed', tags=['Feed'])


@feed_router.get('/')
async def get_feed(
        post_service: PostService = Depends(get_post_service),
        user_id: int = Depends(get_user),
        page_size: int = Query(100, alias='n'),
        page_number: int = Query(0, alias='p')
) -> list[int]:
    """
    Gets the user's feed
    :param post_service: post service
    :param user_id: user ID
    :param page_size: max number of posts to return (for pagination, default=100)
    :param page_number: page number (for pagination, default=0)
    :return: list of posts in the user's feed in descending chronological order
    """
    return await post_service.get_user_feed(user_id, page_size, page_number)
