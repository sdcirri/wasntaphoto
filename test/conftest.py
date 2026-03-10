import os

import httpx
import pytest
import pytest_asyncio

os.environ['DATABASE_URL'] = 'postgresql+psycopg://test:test@localhost/test'

from app import app
from providers.repositories import get_user_repository, get_session_repository


class _FakeUserRepo:
    def __init__(self):
        self._next_id = 1
        self._by_username = {}

    async def find_by_username(self, username: str):
        return self._by_username.get(username)

    async def save(self, user):
        if not getattr(user, 'user_id', None):
            user.user_id = self._next_id
            self._next_id += 1
        self._by_username[user.username] = user
        return user

    async def find_by_id(self, user_id: int, load_posts: bool = False):
        for user in self._by_username.values():
            if user.user_id == user_id:
                return user
        return None


class _FakeSessionRepo:
    def __init__(self):
        self._by_id = {}

    async def find_all(self):
        return list(self._by_id.keys())

    async def save(self, session):
        session_id = session.session_id
        session.session_id = session_id
        self._by_id[session_id] = session

    async def find_by_id(self, session_id: str):
        return self._by_id.get(session_id)

    async def delete(self, session):
        session_id = session.session_id
        self._by_id.pop(session_id, None)


@pytest.fixture(autouse=True)
def _override_repositories():
    user_repo = _FakeUserRepo()
    session_repo = _FakeSessionRepo()

    app.dependency_overrides[get_user_repository] = lambda: user_repo
    app.dependency_overrides[get_session_repository] = lambda: session_repo
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client
