from redis.asyncio import Redis
from httpx import AsyncClient
from hashlib import sha1
import secrets
import string
import pytest

from db.entities import UserModel
from service import AuthService

from .fixtures.users import BAD_PASSWORDS, BAD_AUTH_HEADERS, UserApiSetup


@pytest.mark.asyncio
async def test_login_with_empty_credentials_is_rejected(client: AsyncClient):
    resp = await client.post('/session/', json={'username': '', 'password': ''})
    assert resp.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'password',
    BAD_PASSWORDS
)
async def test_register_with_weak_password_is_rejected(client: AsyncClient, password: str):
    resp = await client.post('/users/', json={'username': 'bob', 'password': password})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_register_with_too_short_password_is_rejected_before_validation(client: AsyncClient):
    resp = await client.post('/users/', json={'username': 'bob', 'password': 'a' * 7})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_with_too_long_password_is_rejected_before_validation(client: AsyncClient):
    resp = await client.post('/users/', json={'username': 'bob', 'password': 'a' * 256})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_with_valid_credentials_returns_token(client: AsyncClient):
    resp = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})

    assert resp.status_code == 200
    assert isinstance(resp.json(), str)
    assert resp.json()


@pytest.mark.asyncio
async def test_login_with_wrong_username_is_rejected(client: AsyncClient, registered_user: str):
    resp = await client.post('/session/', json={'username': 'nobody', 'password': 'wrong!!!'})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_login_with_wrong_password_is_rejected(client: AsyncClient, registered_user: str):
    resp = await client.post('/session/', json={'username': 'bob', 'password': 'wrong!!!'})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_registering_duplicate_username_is_rejected(client: AsyncClient, registered_user: str):
    resp = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_with_correct_credentials_returns_token(client: AsyncClient, registered_user: str):
    resp = await client.post('/session/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})

    assert resp.status_code == 200
    assert isinstance(resp.json(), str)
    assert resp.json()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'bad_header',
    BAD_AUTH_HEADERS
)
async def test_malformed_tokens_are_rejected(client: AsyncClient, registered_user: str, bad_header: str):
    resp = await client.get('/users/me', headers={'Authorization': bad_header})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_expired_tokens_are_rejected(client: AsyncClient, registered_user_with_expired_session: str):
    resp = await client.get('/users/me', headers={'Authorization': f'Bearer {registered_user_with_expired_session}'})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_malformed_credentials_on_db_block_login(client: AsyncClient, user_with_malformed_password_hash: UserModel):
    user = user_with_malformed_password_hash
    resp = await client.post('/session/', json={'username': user.username, 'password': '$up3rS33kr3t!!!!'})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_revoke_session_revokes_session(client: AsyncClient, registered_user: str):
    session = registered_user
    resp = await client.delete(f'/session/{session}', headers={'Authorization': f'Bearer {session}'})
    assert resp.status_code == 204
    resp = await client.get('/users/me', headers={'Authorization': f'Bearer {session}'})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_revoke_session_ignores_nonexisting_session(user_api_setup: UserApiSetup):
    s = user_api_setup
    nonexisting = secrets.token_urlsafe(32)
    while nonexisting == s.alice_session:
        nonexisting = secrets.token_urlsafe(32)
    resp = await s.client.delete(f'/session/{nonexisting}', headers=s.alice_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
@pytest.mark.real_hibp
async def test_hibp_lookup(fake_auth_service: AuthService):
    weak = 'password'
    strong = ''.join(secrets.choice(string.printable[:-6]) for _ in range(24))

    res = await fake_auth_service.hibp_lookup(weak)
    assert res is True
    res = await fake_auth_service.hibp_lookup(strong)
    assert res is False


@pytest.mark.asyncio
@pytest.mark.real_hibp
async def test_hibp_lookup_is_cached(override_redis: Redis, fake_auth_service: AuthService):
    weak = 'password'
    digest = sha1(weak.encode()).hexdigest().upper()
    prefix = digest[:5]
    expected_key = f'{AuthService.REDIS_HIBP_PREFIX}:{prefix}'

    assert await override_redis.get(expected_key) is None

    res = await fake_auth_service.hibp_lookup(weak)
    assert res is True
    assert await override_redis.get(expected_key) is not None
