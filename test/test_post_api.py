from model import PostRequest, Post
import base64
import pytest

from test.fixtures.posts import PostInteractionSetup, PostCrudSetup


def _like_url(s: PostInteractionSetup) -> str:
    return f'/users/{s.author.user_id}/posts/{s.post.post_id}/like'


def _likes_url(s: PostInteractionSetup) -> str:
    return f'/users/me/posts/{s.post.post_id}/likes'


def _post_url(s: PostInteractionSetup) -> str:
    return f'/users/me/posts/{s.post.post_id}'


@pytest.mark.asyncio
async def test_create_post_returns_expected_fields(post_crud_setup: PostCrudSetup, solid_black: bytes):
    s = post_crud_setup
    req = PostRequest(image=base64.b64encode(solid_black), caption='A nice pixel')
    resp = await s.client.post('/users/me/posts/', json=req.model_dump(mode='json'), headers=s.headers)

    assert resp.status_code == 200
    info = Post.model_validate(resp.json())
    assert info.author_id == s.user.user_id
    assert info.caption == 'A nice pixel'
    assert info.image


@pytest.mark.asyncio
async def test_get_post_returns_created_post(post_crud_setup: PostCrudSetup, created_post: Post):
    s = post_crud_setup
    resp = await s.client.get(f'/users/me/posts/{created_post.post_id}', headers=s.headers)

    assert resp.status_code == 200
    assert Post.model_validate(resp.json()) == created_post


@pytest.mark.asyncio
async def test_delete_post_removes_it(post_crud_setup: PostCrudSetup, created_post: Post):
    s = post_crud_setup
    del_resp = await s.client.delete(f'/users/me/posts/{created_post.post_id}', headers=s.headers)
    assert del_resp.status_code == 204

    get_resp = await s.client.get(f'/users/me/posts/{created_post.post_id}', headers=s.headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_liking_post_increments_like_count(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.get(_post_url(s), headers=s.author_auth)

    assert resp.status_code == 200
    assert Post.model_validate(resp.json()).like_cnt == 2


@pytest.mark.asyncio
async def test_author_can_see_who_liked_post(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.get(_likes_url(s), headers=s.author_auth)

    assert resp.status_code == 200
    assert set(resp.json()) == {s.user.user_id, s.author.user_id}


@pytest.mark.asyncio
async def test_non_author_cannot_see_who_liked_post(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.get(_likes_url(s), headers=s.user_auth)

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unliking_post_removes_user_from_likes(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    unlike_resp = await s.client.delete(_like_url(s), headers=s.user_auth)
    assert unlike_resp.status_code == 204

    likes_resp = await s.client.get(_likes_url(s), headers=s.author_auth)
    assert likes_resp.status_code == 200
    assert set(likes_resp.json()) == {s.author.user_id}
