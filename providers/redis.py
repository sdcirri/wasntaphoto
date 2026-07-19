from redis.asyncio import Redis
from os import getenv


redis_url = getenv('REDIS_URL')
if not redis_url:
    raise RuntimeError('REDIS_URL is not set, exiting ...')


_REDIS: Redis | None = None


def get_redis() -> Redis:
    assert _REDIS is not None
    return _REDIS


async def connect_redis() -> None:
    global _REDIS
    _REDIS = Redis.from_url(redis_url, decode_responses=True)
    assert _REDIS is not None
    await _REDIS.ping()


async def disconnect_redis() -> None:
    global _REDIS
    if _REDIS is not None:
        await _REDIS.aclose()
        _REDIS = None
