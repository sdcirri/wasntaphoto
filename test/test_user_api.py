import pytest


@pytest.mark.asyncio
async def test_user_api(client, user_factory):
    await user_factory('alice', 'H@xx0r.2026')
    await user_factory('bob', 'T0P.S3cr3t!')

    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    token = login.json()

    alice_info = await client.get('/users/1', headers={'Authorization': f'Bearer {token}'})
    assert alice_info.status_code == 200
    assert alice_info.json()['username'] == 'alice'
    assert alice_info.json()['user_id'] == 1

    me_info = await client.get('/users/me', headers={'Authorization': f'Bearer {token}'})
    assert me_info.status_code == 200
    assert me_info.json()['username'] == 'alice'
    assert me_info.json()['user_id'] == 1

    bob_info = await client.get('/users/2', headers={'Authorization': f'Bearer {token}'})
    assert bob_info.status_code == 200
    assert bob_info.json()['username'] == 'bob'
    assert bob_info.json()['user_id'] == 2

    username_change = await client.put('/users/me/username', json='@lix', headers={'Authorization': f'Bearer {token}'})
    assert username_change.status_code == 204
    me_info = await client.get('/users/me', headers={'Authorization': f'Bearer {token}'})
    assert me_info.json()['username'] == '@lix'
