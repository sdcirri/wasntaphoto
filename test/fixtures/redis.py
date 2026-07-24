from typing import Any, Generator, AsyncGenerator
from testcontainers.redis import RedisContainer
from redis.asyncio import Redis
import pytest_asyncio
import pytest
import os

from providers.redis import connect_redis_from_env


@pytest.fixture(scope='session', autouse=True)
def redis_container() -> Generator[RedisContainer, Any, None]:
    with RedisContainer('redis:8-alpine') as container:
        os.environ['REDIS_URL'] = f'redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}/0'
        yield container


@pytest_asyncio.fixture(scope='session')
async def redis_client(redis_container: RedisContainer) -> AsyncGenerator[Redis, None]:
    client = await connect_redis_from_env()
    yield client
    await client.aclose()


@pytest_asyncio.fixture(autouse=True)
async def _clean_redis(redis_client: Redis) -> AsyncGenerator[None, None]:
    yield
    await redis_client.flushdb()
