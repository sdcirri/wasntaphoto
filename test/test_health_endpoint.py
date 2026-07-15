from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_health_endpoint_is_success(client: AsyncClient):
    resp = await client.get('/liveness')
    assert resp.status_code == 200
