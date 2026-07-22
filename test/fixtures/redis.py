from typing import Any, Generator, AsyncGenerator
from testcontainers.redis import RedisContainer
from redis.asyncio import Redis
import pytest_asyncio
import pytest

import providers.redis as redis_provider
from providers.redis import get_redis
from app import app


@pytest.fixture(scope='session')
def redis_container() -> Generator[RedisContainer, Any, None]:
    with RedisContainer('redis:8-alpine') as container:
        yield container


def _redis_url(container: RedisContainer) -> str:
    host = container.get_container_host_ip()
    port = container.get_exposed_port(6379)
    return f'redis://{host}:{port}/0'


@pytest_asyncio.fixture(scope='session')
async def redis_client(redis_container: RedisContainer) -> AsyncGenerator[Redis, None]:
    client = Redis.from_url(_redis_url(redis_container), decode_responses=True)
    await client.ping()
    yield client
    await client.aclose()


@pytest_asyncio.fixture(autouse=True)
async def override_redis(
        monkeypatch: pytest.MonkeyPatch,
        redis_client: Redis,
        redis_container: RedisContainer,
) -> AsyncGenerator[Redis, None]:
    monkeypatch.setattr(redis_provider, 'redis_url', _redis_url(redis_container))

    async def connect_redis() -> None:
        redis_provider._REDIS = redis_client
        await redis_client.ping()

    async def disconnect_redis() -> None:
        redis_provider._REDIS = None

    monkeypatch.setattr(redis_provider, 'connect_redis', connect_redis)
    monkeypatch.setattr(redis_provider, 'disconnect_redis', disconnect_redis)
    monkeypatch.setattr('app.connect_redis', connect_redis)
    monkeypatch.setattr('app.disconnect_redis', disconnect_redis)

    redis_provider._REDIS = redis_client

    def _get_redis() -> Redis:
        return redis_client

    app.dependency_overrides[get_redis] = _get_redis

    try:
        yield redis_client
    finally:
        app.dependency_overrides.pop(get_redis, None)
        redis_provider._REDIS = None


@pytest_asyncio.fixture(autouse=True)
async def _clean_redis(redis_client: Redis) -> AsyncGenerator[None, None]:
    yield
    await redis_client.flushdb()
