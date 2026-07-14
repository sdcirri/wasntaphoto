from random import randint
import pytest

from model import UserAccount

from .fixtures.users import UserApiSetup, FollowingSetup
from .conftest import rmsdiff


@pytest.mark.asyncio
async def test_text_search_on_usernames(extra_users_for_search: UserApiSetup):
    s = extra_users_for_search
    resp = await s.client.get('/users/?q=USE&limit=10')
    assert resp.status_code == 200
    assert len(resp.json()) == 10
    for i in resp.json():
        assert isinstance(i, int)
        info = await s.client.get(f'/users/{i}', headers=s.headers)
        assert info.status_code == 200
        assert UserAccount.model_validate(info.json()).username.lower().startswith('use')


@pytest.mark.asyncio
async def test_text_search_is_bounded(extra_users_for_search: UserApiSetup):
    s = extra_users_for_search
    resp = await s.client.get('/users/?q=use&limit=10')
    assert len(resp.json()) == 10
    resp = await s.client.get('/users/?q=use&limit=20')
    assert len(resp.json()) == 20


@pytest.mark.asyncio
async def test_text_search_default_limit_is_10(extra_users_for_search: UserApiSetup):
    s = extra_users_for_search
    resp = await s.client.get('/users/?q=use')
    assert len(resp.json()) == 10


@pytest.mark.asyncio
async def test_get_own_profile_by_id(user_api_setup: UserApiSetup):
    s = user_api_setup
    resp = await s.client.get(f'/users/{s.alice.user_id}', headers=s.headers)

    assert resp.status_code == 200
    assert resp.json()['username'] == 'alice'
    assert resp.json()['user_id'] == s.alice.user_id


@pytest.mark.asyncio
async def test_get_me_returns_own_profile(user_api_setup: UserApiSetup):
    s = user_api_setup
    resp = await s.client.get('/users/me', headers=s.headers)

    assert resp.status_code == 200
    info = UserAccount.model_validate(resp.json())
    assert info.username == 'alice'
    assert info.user_id == s.alice.user_id


@pytest.mark.asyncio
async def test_get_other_users_profile_by_id(user_api_setup: UserApiSetup):
    s = user_api_setup
    resp = await s.client.get(f'/users/{s.bob.user_id}', headers=s.headers)

    assert resp.status_code == 200
    info = UserAccount.model_validate(resp.json())
    assert info.username == 'bob'
    assert info.user_id == s.bob.user_id


@pytest.mark.asyncio
async def test_get_nonexistent_user_returns_404(user_api_setup: UserApiSetup):
    s = user_api_setup
    bad_id = randint(1, 1_000_000_000)
    while bad_id in (s.alice.user_id, s.bob.user_id):
        bad_id = randint(1, 1_000_000_000)

    resp = await s.client.get(f'/users/{bad_id}', headers=s.headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_change_username_updates_profile(user_api_setup: UserApiSetup):
    s = user_api_setup
    change_resp = await s.client.put('/users/me/username', json='@lix', headers=s.headers)
    assert change_resp.status_code == 204

    me_resp = await s.client.get('/users/me', headers=s.headers)
    assert me_resp.json()['username'] == '@lix'


@pytest.mark.asyncio
async def test_change_username_rejects_username_already_taken(user_api_setup: UserApiSetup):
    s = user_api_setup
    change_resp = await s.client.put('/users/me/username', json='bob', headers=s.headers)
    assert change_resp.status_code == 409

    me_resp = await s.client.get('/users/me', headers=s.headers)
    assert me_resp.json()['username'] == 'alice'


@pytest.mark.asyncio
async def test_change_profile_picture_updates_propic(user_api_setup: UserApiSetup, checkerboard: bytes):
    s = user_api_setup
    change_resp = await s.client.put(
        '/users/me/pp',
        content=checkerboard,
        headers=s.headers | {'Content-Type': 'image/png'}
    )
    assert change_resp.status_code == 204

    me_resp = await s.client.get('/users/me', headers=s.headers)
    assert rmsdiff(UserAccount.model_validate(me_resp.json()).propic, checkerboard) < 10


@pytest.mark.asyncio
async def test_new_user_follows_nobody(following_setup: FollowingSetup):
    s = following_setup
    resp = await s.client.get('/users/me/following', headers=s.alice_headers)

    assert resp.status_code == 200
    assert not resp.json()


@pytest.mark.asyncio
async def test_following_user_adds_to_following_list(alice_following_bob: FollowingSetup):
    s = alice_following_bob
    resp = await s.client.get('/users/me/following', headers=s.alice_headers)
    assert s.bob.user_id in resp.json()


@pytest.mark.asyncio
async def test_following_user_adds_follower_to_their_list(alice_following_bob: FollowingSetup):
    s = alice_following_bob
    resp = await s.client.get('/users/me/followers', headers=s.bob_headers)
    assert s.alice.user_id in resp.json()


@pytest.mark.asyncio
async def test_unfollowing_user_removes_from_following_list(alice_following_bob: FollowingSetup):
    s = alice_following_bob
    unfollow_resp = await s.client.delete(f'/users/me/following/{s.bob.user_id}', headers=s.alice_headers)
    assert unfollow_resp.status_code == 204

    following_resp = await s.client.get('/users/me/following', headers=s.alice_headers)
    assert s.bob.user_id not in following_resp.json()


@pytest.mark.asyncio
async def test_blocking_user_adds_to_blocked_list(alice_blocked_annoying: FollowingSetup):
    s = alice_blocked_annoying
    resp = await s.client.get('/users/me/blocked', headers=s.alice_headers)

    assert resp.status_code == 200
    assert s.annoying.user_id in resp.json()


@pytest.mark.asyncio
async def test_blocking_followed_user_removes_them_from_following(alice_blocked_annoying: FollowingSetup):
    s = alice_blocked_annoying
    resp = await s.client.get('/users/me/following', headers=s.alice_headers)
    assert s.annoying.user_id not in resp.json()


@pytest.mark.asyncio
async def test_blocked_user_cannot_view_blocker_profile(alice_blocked_annoying: FollowingSetup):
    s = alice_blocked_annoying
    resp = await s.client.get(f'/users/{s.alice.user_id}', headers=s.annoying_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_blocked_user_cannot_view_blocker_posts(alice_blocked_annoying: FollowingSetup):
    s = alice_blocked_annoying
    resp = await s.client.get(f'/users/{s.alice.user_id}/posts/', headers=s.annoying_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unblocking_user_removes_from_blocked_list(alice_blocked_annoying: FollowingSetup):
    s = alice_blocked_annoying
    unblock_resp = await s.client.delete(f'/users/me/blocked/{s.annoying.user_id}', headers=s.alice_headers)
    assert unblock_resp.status_code == 204

    blocked_resp = await s.client.get('/users/me/blocked', headers=s.alice_headers)
    assert s.annoying.user_id not in blocked_resp.json()


@pytest.mark.asyncio
async def test_cannot_follow_yourself(following_setup: FollowingSetup):
    s = following_setup
    resp = await s.client.post(f'/users/me/following/{s.alice.user_id}', headers=s.alice_headers)
    assert resp.status_code == 400
