from redis.asyncio import Redis
from fastapi import Request
from os import getenv


async def connect_redis_from_env() -> Redis:
    redis_url = getenv('REDIS_URL')
    if not redis_url:
        raise RuntimeError('REDIS_URL is not set, exiting ...')
    redis = Redis.from_url(redis_url, decode_responses=True)
    await redis.ping()
    return redis


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
