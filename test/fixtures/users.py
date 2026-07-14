from httpx import AsyncClient
import pytest_asyncio


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> None:
    """
    Registers 'bob' with a valid password. Used by tests that need
    an existing account already in place.
    """

    resp = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})
    assert resp.status_code == 200
