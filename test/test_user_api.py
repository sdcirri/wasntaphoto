from typing import Callable, Coroutine, Any
from httpx import AsyncClient
import asyncio
import pytest

from db.entities import UserModel


@pytest.mark.asyncio
async def test_user_api(client: AsyncClient, user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]]):
    alice_user, bob_user = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'T0P.S3cr3t!')
    )

    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    headers = {'Authorization': f'Bearer {login.json()}'}

    alice_info = await client.get(f'/users/{alice_user.user_id}', headers=headers)
    assert alice_info.status_code == 200
    assert alice_info.json()['username'] == 'alice'
    assert alice_info.json()['user_id'] == alice_user.user_id

    me_info = await client.get('/users/me', headers=headers)
    assert me_info.status_code == 200
    assert me_info.json()['username'] == 'alice'
    assert me_info.json()['user_id'] == alice_user.user_id

    bob_info = await client.get(f'/users/{bob_user.user_id}', headers=headers)
    assert bob_info.status_code == 200
    assert bob_info.json()['username'] == 'bob'
    assert bob_info.json()['user_id'] == bob_user.user_id

    username_change = await client.put('/users/me/username', json='@lix', headers=headers)
    assert username_change.status_code == 204
    me_info = await client.get('/users/me', headers=headers)
    assert me_info.json()['username'] == '@lix'


@pytest.mark.asyncio
async def test_following_mechanics(client: AsyncClient, user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]]):
    alice_user, bob_user, annoying_user = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'T0P.S3cr3t!'),
        user_factory('annoying', 'I@mAnn0ying!')
    )
    alice_login, bob_login, annoying_login = await asyncio.gather(
        client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'}),
        client.post('/session/', json={'username': 'bob', 'password': 'T0P.S3cr3t!'}),
        client.post('/session/', json={'username': 'annoying', 'password': 'I@mAnn0ying!'})
    )
    alice_headers, bob_headers, annoying_headers = (
        {'Authorization': f'Bearer {alice_login.json()}'},
        {'Authorization': f'Bearer {bob_login.json()}'},
        {'Authorization': f'Bearer {annoying_login.json()}'}
    )

    following = await client.get('/users/me/following', headers=alice_headers)
    assert following.status_code == 200
    assert not following.json()

    await client.post(f'/users/me/following/{bob_user.user_id}', headers=alice_headers)
    following, followers = await asyncio.gather(
        client.get('/users/me/following', headers=alice_headers),
        client.get('/users/me/followers', headers=bob_headers)
    )
    assert bob_user.user_id in following.json()
    assert alice_user.user_id in followers.json()

    unfollow = await client.delete(f'/users/me/following/{bob_user.user_id}', headers=alice_headers)
    assert unfollow.status_code == 204
    following = await client.get('/users/me/following', headers=alice_headers)
    assert bob_user.user_id not in following.json()

    await client.post(f'/users/me/following/{annoying_user.user_id}', headers=alice_headers)
    await client.post(f'/users/me/blocked/{annoying_user.user_id}', headers=alice_headers)
    blocked = await client.get('/users/me/blocked', headers=alice_headers)
    assert blocked.status_code == 200
    assert annoying_user.user_id in blocked.json()
    following = await client.get('/users/me/following', headers=alice_headers)
    assert annoying_user.user_id not in following.json()

    profile = await client.get(f'/users/{alice_user.user_id}', headers=annoying_headers)
    assert profile.status_code == 403

    posts = await client.get(f'/users/{alice_user.user_id}/posts/', headers=annoying_headers)
    assert posts.status_code == 403

    unblock = await client.delete(f'/users/me/blocked/{annoying_user.user_id}', headers=alice_headers)
    assert unblock.status_code == 204
    blocked = await client.get('/users/me/blocked', headers=alice_headers)
    assert annoying_user.user_id not in blocked.json()

    bad_follow = await client.post(f'/users/me/following/{alice_user.user_id}', headers=alice_headers)
    assert bad_follow.status_code == 400
