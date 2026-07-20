from fastapi import Depends, Request, Response
from pyrate_limiter import Rate, Duration
from redis.asyncio import Redis

from security.rate_limiting import do_rl

from .redis import get_redis


async def liveness_limiter(request: Request, response: Response, redis: Redis = Depends(get_redis)) -> None:
    await do_rl(Rate(2, Duration.SECOND), 'ratelimit:liveness', request, response, redis)


async def read_limiter(request: Request, response: Response, redis: Redis = Depends(get_redis)) -> None:
    await do_rl(Rate(240, Duration.MINUTE), 'ratelimit:read', request, response, redis)


async def auth_limiter(request: Request, response: Response, redis: Redis = Depends(get_redis)) -> None:
    await do_rl(Rate(10, Duration.MINUTE), 'ratelimit:auth', request, response, redis)


async def user_edit_limiter(request: Request, response: Response, redis: Redis = Depends(get_redis)) -> None:
    await do_rl(Rate(20, Duration.MINUTE), 'ratelimit:user', request, response, redis)


async def post_limiter(request: Request, response: Response, redis: Redis = Depends(get_redis)) -> None:
    await do_rl(Rate(20, Duration.MINUTE), 'ratelimit:post', request, response, redis)


async def comment_limiter(request: Request, response: Response, redis: Redis = Depends(get_redis)) -> None:
    await do_rl(Rate(40, Duration.MINUTE), 'ratelimit:comment', request, response, redis)
