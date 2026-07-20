from pyrate_limiter import Limiter, Rate, RedisBucket, BucketAsyncWrapper
from fastapi_limiter.depends import RateLimiter
from fastapi import Request, Response
from redis.asyncio import Redis

from exceptions import BadAuthError, SessionExpiredError
from service import AuthService


async def limiter(rate: Rate, redis: Redis, key: str) -> Limiter:
    bucket = await RedisBucket.init([rate], redis, key)
    return Limiter(BucketAsyncWrapper(bucket))


async def do_rl(rate: Rate, key: str, request: Request, response: Response, redis: Redis) -> None:
    async def rl_identifier(request_: Request) -> str:
        """
        Computes request identifier (IP + user ID if authenticated)
        for rate limiting purposes
        :param request_: raw request
        :return: the request identifier
        """
        ip = request_.headers.get('X-Forwarded-For', request_.client.host).split(',')[0].strip()
        token = request_.headers.get('Authorization', '').lower().removeprefix('bearer')
        if token:
            try:
                user_id = await redis.get(f'{AuthService.REDIS_TOKEN_PREFIX}:{token}')
            except (BadAuthError, SessionExpiredError):
                user_id = 'anon'
        else:
            user_id = 'anon'

        return f'{ip}:{user_id}'

    limit = await limiter(rate, redis, key)
    rl = RateLimiter(limit, identifier=rl_identifier)
    await rl(request, response)
