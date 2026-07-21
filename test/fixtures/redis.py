from typing import AsyncIterator, Any
from unittest.mock import AsyncMock
import pytest_asyncio
import fakeredis
import pytest
import inspect

from providers.redis import get_redis
from app import app


@pytest_asyncio.fixture
async def redis_client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    redis = fakeredis.aioredis.FakeRedis(
        decode_responses=True,
    )

    await redis.flushall()

    real_get = redis.get
    real_set = redis.set
    real_delete = redis.delete

    async def wrapped_get(*args: Any, **kwargs: Any):
        result = real_get(*args, **kwargs)

        if inspect.isawaitable(result):
            return await result

        return result

    async def wrapped_set(*args: Any, **kwargs: Any):
        result = real_set(*args, **kwargs)

        if inspect.isawaitable(result):
            return await result

        return result

    async def wrapped_delete(*args: Any, **kwargs: Any):
        result = real_delete(*args, **kwargs)

        if inspect.isawaitable(result):
            return await result

        return result

    async def fake_connect():
        return None

    async def fake_disconnect():
        return None

    monkeypatch.setattr('app.connect_redis', fake_connect)
    monkeypatch.setattr('app.disconnect_redis', fake_disconnect)

    get_spy = AsyncMock(side_effect=wrapped_get)
    set_spy = AsyncMock(side_effect=wrapped_set)
    delete_spy = AsyncMock(side_effect=wrapped_delete)

    redis.get = get_spy
    redis.set = set_spy
    redis.delete = delete_spy

    try:
        yield redis
    finally:
        await redis.aclose()


@pytest_asyncio.fixture(autouse=True)
async def override_redis(redis_client: AsyncIterator[fakeredis.aioredis.FakeRedis]) -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    def get_fake_redis():
        return redis_client

    app.dependency_overrides[get_redis] = get_fake_redis

    try:
        yield redis_client
    finally:
        app.dependency_overrides.pop(get_redis, None)
