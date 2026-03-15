from typing import AsyncGenerator
import pytest_asyncio
import httpx

from app import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client
