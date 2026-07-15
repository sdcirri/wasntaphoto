from typing import Callable, Any, Coroutine
from types import SimpleNamespace
from httpx import AsyncClient
import pytest_asyncio
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db.entities import UserModel
from service import AuthService


class UserApiSetup(SimpleNamespace):
    client: AsyncClient
    alice: UserModel
    bob: UserModel
    headers: dict[str, str]


class FollowingSetup(SimpleNamespace):
    client: AsyncClient
    alice: UserModel
    bob: UserModel
    annoying: UserModel
    alice_headers: dict[str, str]
    bob_headers: dict[str, str]
    annoying_headers: dict[str, str]


@pytest_asyncio.fixture
async def user_api_setup(
        client: AsyncClient,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
) -> UserApiSetup:
    """
    Registers alice and bob, and logs in as alice.
    """

    alice, bob = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'T0P.S3cr3t!'),
    )
    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    headers = {'Authorization': f'Bearer {login.json()}'}
    return UserApiSetup(client=client, alice=alice, bob=bob, headers=headers)


@pytest_asyncio.fixture
async def following_setup(
        client: AsyncClient,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
) -> FollowingSetup:
    """
    Registers and logs in three users: alice, bob, and annoying.
    """

    alice, bob, annoying = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'T0P.S3cr3t!'),
        user_factory('annoying', 'I@mAnn0ying!'),
    )
    alice_login, bob_login, annoying_login = await asyncio.gather(
        client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'}),
        client.post('/session/', json={'username': 'bob', 'password': 'T0P.S3cr3t!'}),
        client.post('/session/', json={'username': 'annoying', 'password': 'I@mAnn0ying!'}),
    )
    return FollowingSetup(
        client=client,
        alice=alice, bob=bob, annoying=annoying,
        alice_headers={'Authorization': f'Bearer {alice_login.json()}'},
        bob_headers={'Authorization': f'Bearer {bob_login.json()}'},
        annoying_headers={'Authorization': f'Bearer {annoying_login.json()}'},
    )


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> None:
    """
    Registers 'bob' with a valid password. Used by tests that need
    an existing account already in place.
    """

    resp = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})
    assert resp.status_code == 200


@pytest_asyncio.fixture
async def alice_following_bob(following_setup: FollowingSetup) -> FollowingSetup:
    """
    Builds on following_setup with alice already following bob.
    """

    s = following_setup
    resp = await s.client.post(f'/users/me/following/{s.bob.user_id}', headers=s.alice_headers)
    assert resp.status_code in (200, 204)
    return s


@pytest_asyncio.fixture
async def alice_blocked_annoying(following_setup: FollowingSetup) -> FollowingSetup:
    """
    Builds on following_setup with alice following, then blocking, annoying.
    """

    s = following_setup
    await s.client.post(f'/users/me/following/{s.annoying.user_id}', headers=s.alice_headers)
    resp = await s.client.post(f'/users/me/blocked/{s.annoying.user_id}', headers=s.alice_headers)
    assert resp.status_code in (200, 204)
    return s


@pytest_asyncio.fixture
async def extra_users_for_search(_sqlite_database: async_sessionmaker[AsyncSession]) -> None:
    """
    Creates a bunch of users with similar usernames for testing search mechanics
    """

    password_hash = AuthService.ph.hash("$up3rS33kr3t!!!!")
    users = [
        UserModel(
            username=username,
            password=password_hash,
        )
        for i in range(20)
        for username in (f'bob{i}', f'user{i}')
    ]
    async with _sqlite_database() as session:
        session.add_all(users)
        await session.commit()


@pytest_asyncio.fixture
async def search_setup(user_api_setup: UserApiSetup, extra_users_for_search: None) -> UserApiSetup:
    return user_api_setup
