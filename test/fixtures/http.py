from typing import AsyncGenerator
import pytest_asyncio
import pytest
import httpx

from service import AuthService
from app import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mock_hibp(request, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker("real_hibp"):
        return

    async def fake_hibp_lookup(
        self: AuthService,
        password: str,
    ) -> bool:
        return password == 'Password.1'

    monkeypatch.setattr(
        AuthService,
        'hibp_lookup',
        fake_hibp_lookup,
    )
