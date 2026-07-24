from httpx import AsyncClient
import pytest

from app import app, lifespan


@pytest.mark.asyncio
async def test_app_lifespan(client: AsyncClient):
    async with lifespan(app):
        resp = await client.get('/liveness')
        assert resp.status_code == 200
