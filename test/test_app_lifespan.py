from typing import AsyncIterator
import fakeredis
import pytest
import httpx

from app import app, lifespan


@pytest.mark.asyncio
async def test_app_lifespan(override_redis: AsyncIterator[fakeredis.aioredis.FakeRedis]):
    async with lifespan(app):
        async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://test",
        ) as client:
            resp = await client.get('/liveness')
            assert resp.status_code == 200
