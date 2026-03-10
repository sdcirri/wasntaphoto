import pytest


@pytest.mark.asyncio
async def test_login_api(client):
    invalid_login = await client.post('/session/', json={'username': '', 'password': ''})
    assert invalid_login.status_code == 422

    weak_register = await client.post('/users/', json={'username': 'bob', 'password': 'secret'})
    assert weak_register.status_code == 422

    register = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})
    assert register.status_code == 200
    assert isinstance(register.json(), str)
    assert register.json()

    wrong_login = await client.post('/session/', json={'username': 'bob', 'password': 'wrong!!!'})
    assert wrong_login.status_code == 403

    double_register = await client.post('/users/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})
    assert double_register.status_code == 409

    login = await client.post('/session/', json={'username': 'bob', 'password': '$up3rS33kr3t!!!!'})
    assert login.status_code == 200
    assert isinstance(login.json(), str)
    assert login.json()
