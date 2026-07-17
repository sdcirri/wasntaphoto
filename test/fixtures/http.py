from typing import AsyncGenerator
import pytest_asyncio
import pytest
import httpx

from app import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client


@pytest_asyncio.fixture(autouse=True)
def mock_hibp(request, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker('real_hibp'):
        return
    async def fake_hibp_lookup(password: str) -> bool:
        return password == 'Password.1'
    monkeypatch.setattr('service.auth_service.AuthService.hibp_lookup', staticmethod(fake_hibp_lookup))
