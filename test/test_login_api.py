from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_login_with_empty_credentials_is_rejected(client: AsyncClient):
    resp = await client.post('/session/', json={'username': '', 'password': ''})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_with_weak_password_is_rejected(client: AsyncClient):
    resp = await client.post('/users/', json={'username': 'bob', 'password': 'secret'})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_with_valid_credentials_returns_token(client: AsyncClient):
    resp = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})

    assert resp.status_code == 200
    assert isinstance(resp.json(), str)
    assert resp.json()


@pytest.mark.asyncio
async def test_login_with_wrong_password_is_rejected(client: AsyncClient, registered_user: None):
    resp = await client.post('/session/', json={'username': 'bob', 'password': 'wrong!!!'})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_registering_duplicate_username_is_rejected(client: AsyncClient, registered_user: None):
    resp = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_with_correct_credentials_returns_token(client: AsyncClient, registered_user: None):
    resp = await client.post('/session/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})

    assert resp.status_code == 200
    assert isinstance(resp.json(), str)
    assert resp.json()
