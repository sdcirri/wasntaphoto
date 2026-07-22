from fastapi import APIRouter, Depends

from providers.rate_limiting import read_limiter


media_router = APIRouter(prefix='/media', tags=['Media'], dependencies=[Depends(read_limiter)])


@media_router.get('/posts/{post_id}')
async def get_post_image(post_id: int) -> bytes:
    pass


@media_router.get('/propics/{user_id}')
async def get_propic(user_id: int) -> bytes:
    pass
