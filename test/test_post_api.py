from typing import Callable, Any, Coroutine
from minio import Minio
import base64
import pytest

from db.entities import UserModel, PostModel
from model import PostRequest, Post
from service.storage_service import StorageService

from .fixtures.posts import PostInteractionSetup, PostCrudSetup
from .fixtures.users import FollowingSetup
from .conftest import rmsdiff


def _like_url(s: PostInteractionSetup) -> str:
    return f'/users/{s.author.user_id}/posts/{s.post.post_id}/like'


def _likes_url(s: PostInteractionSetup) -> str:
    return f'/users/me/posts/{s.post.post_id}/likes'


def _post_url(s: PostInteractionSetup) -> str:
    return f'/users/me/posts/{s.post.post_id}'


@pytest.mark.asyncio
async def test_target_user_resolver_accepts_ints(post_interaction_setup: PostInteractionSetup):
    s = post_interaction_setup
    resp = await s.client.get(f'/users/{s.author.user_id}/posts/', headers=s.author_auth)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_target_user_resolver_accepts_me(post_interaction_setup: PostInteractionSetup):
    s = post_interaction_setup
    resp = await s.client.get(f'/users/me/posts/', headers=s.author_auth)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_target_user_rejects_bad_strings(post_interaction_setup: PostInteractionSetup):
    s = post_interaction_setup
    resp = await s.client.get(f'/users/gibberish/posts/', headers=s.author_auth)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_post_returns_expected_fields(post_crud_setup: PostCrudSetup, solid_black: bytes):
    s = post_crud_setup
    req = PostRequest(image=base64.b64encode(solid_black), caption='A nice pixel')
    resp = await s.client.post('/users/me/posts/', json=req.model_dump(mode='json'), headers=s.headers)

    assert resp.status_code == 200
    info = Post.model_validate(resp.json())
    assert info.author_id == s.user.user_id
    assert info.caption == 'A nice pixel'


@pytest.mark.asyncio
async def test_create_post_stores_media(post_crud_setup: PostCrudSetup, solid_black: bytes):
    s = post_crud_setup
    req = PostRequest(image=base64.b64encode(solid_black), caption='A nice pixel')
    resp = await s.client.post('/users/me/posts/', json=req.model_dump(mode='json'), headers=s.headers)
    assert resp.status_code == 200
    post = Post.model_validate(resp.json())

    resp = await s.client.get(f'/users/me/posts/{post.post_id}/media', headers=s.headers)
    assert resp.status_code == 200
    assert rmsdiff(solid_black, resp.content) < 6


@pytest.mark.asyncio
async def test_create_post_only_accepts_me_in_path(post_interaction_setup: PostInteractionSetup, solid_black: bytes):
    s = post_interaction_setup
    req = PostRequest(image=base64.b64encode(solid_black), caption='A nice pixel')
    resp = await s.client.post(f'/users/{s.user.user_id}/posts/', json=req.model_dump(mode='json'), headers=s.author_auth)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_post_returns_created_post(post_crud_setup: PostCrudSetup, created_post: Post):
    s = post_crud_setup
    resp = await s.client.get(f'/users/me/posts/{created_post.post_id}', headers=s.headers)

    assert resp.status_code == 200
    assert Post.model_validate(resp.json()) == created_post


@pytest.mark.asyncio
async def test_get_post_rejects_incoherent_user_id_in_path(post_interaction_setup: PostInteractionSetup):
    s = post_interaction_setup
    resp = await s.client.get(f'/users/{s.user.user_id}/posts/{s.post.post_id}', headers=s.user_auth)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_post_media_rejects_nonexisting_post(post_crud_setup: PostCrudSetup):
    s = post_crud_setup
    resp = await s.client.get(f'/users/me/posts/1/media', headers=s.headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_post_media_rejects_incoherent_user_id_in_path(post_interaction_setup: PostInteractionSetup):
    s = post_interaction_setup
    resp = await s.client.get(f'/users/{s.user.user_id}/posts/{s.post.post_id}/media', headers=s.user_auth)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_post_media_rejects_blocked_user(
        alice_blocked_annoying: FollowingSetup,
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]],
        solid_black: bytes
):
    s = alice_blocked_annoying
    post = await post_factory(s.alice.user_id, solid_black, 'A nice pixel')
    resp = await s.client.get(f'/users/{s.alice.user_id}/posts/{post.post_id}/media', headers=s.alice_headers)
    assert resp.status_code == 200
    resp = await s.client.get(f'/users/{s.alice.user_id}/posts/{post.post_id}/media', headers=s.annoying_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_post_media_handles_missing_media(
        post_crud_setup: PostCrudSetup,
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]],
        minio_client: Minio,
        solid_black: bytes
):
    s = post_crud_setup
    post = await post_factory(s.user.user_id, solid_black, 'A nice pixel')
    minio_client.remove_object(StorageService.POST_BUCKET, f'{post.post_id}.jpg')
    resp = await s.client.get(f'/users/{s.user.user_id}/posts/{post.post_id}', headers=s.headers)
    assert resp.status_code == 200
    resp = await s.client.get(f'/users/{s.user.user_id}/posts/{post.post_id}/media', headers=s.headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_removes_it(post_crud_setup: PostCrudSetup, created_post: Post):
    s = post_crud_setup
    del_resp = await s.client.delete(f'/users/me/posts/{created_post.post_id}', headers=s.headers)
    assert del_resp.status_code == 204

    get_resp = await s.client.get(f'/users/me/posts/{created_post.post_id}', headers=s.headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_post_is_ignored(post_crud_setup: PostCrudSetup):
    s = post_crud_setup
    del_resp = await s.client.delete(f'/users/me/posts/1', headers=s.headers)
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_post_only_accepts_me_in_path(
        post_crud_setup: PostCrudSetup,
        created_post: Post,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]]
):
    s = post_crud_setup
    user = await user_factory('bob', 'R@nd0mP@ss!!!1!')
    del_resp = await s.client.delete(f'/users/{user.user_id}/posts/{created_post.post_id}', headers=s.headers)
    assert del_resp.status_code == 400


@pytest.mark.asyncio
async def test_is_liked_returns_post_status(post_crud_setup: PostCrudSetup, created_post: Post):
    s = post_crud_setup
    like_url = f'/users/me/posts/{created_post.post_id}/like'

    resp = await s.client.get(like_url, headers=s.headers)
    assert resp.status_code == 200
    assert resp.json() == False

    resp = await s.client.put(like_url, headers=s.headers)
    assert resp.status_code == 204

    resp = await s.client.get(like_url, headers=s.headers)
    assert resp.status_code == 200
    assert resp.json() == True


@pytest.mark.asyncio
async def test_liking_post_increments_like_count(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.get(_post_url(s), headers=s.author_auth)

    assert resp.status_code == 200
    assert Post.model_validate(resp.json()).like_cnt == 2


@pytest.mark.asyncio
async def test_liking_post_is_idempotent(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.put(_like_url(s), headers=s.user_auth)
    assert resp.status_code == 204
    resp = await s.client.put(_like_url(s), headers=s.user_auth)
    assert resp.status_code == 204
    resp = await s.client.get(_post_url(s), headers=s.author_auth)

    assert resp.status_code == 200
    assert Post.model_validate(resp.json()).like_cnt == 2


@pytest.mark.asyncio
async def test_is_liked_errors_on_post_not_found(post_crud_setup: PostCrudSetup):
    s = post_crud_setup
    resp = await s.client.get('/users/me/posts/1', headers=s.headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_liking_post_errors_on_post_not_found(post_crud_setup: PostCrudSetup):
    s = post_crud_setup
    resp = await s.client.put('/users/me/posts/1/like', headers=s.headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unliking_post_errors_on_post_not_found(post_crud_setup: PostCrudSetup):
    s = post_crud_setup
    resp = await s.client.delete('/users/me/posts/1/like', headers=s.headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_likes_endpoint_requires_me(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.get(f'/users/{s.author.user_id}/posts/{s.post.post_id}/likes', headers=s.author_auth)
    assert resp.status_code == 200
    resp = await s.client.get(f'/users/{s.user.user_id}/posts/{s.post.post_id}/likes', headers=s.author_auth)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_author_can_see_who_liked_post(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.get(_likes_url(s), headers=s.author_auth)

    assert resp.status_code == 200
    assert set(resp.json()) == {s.user.user_id, s.author.user_id}


@pytest.mark.asyncio
async def test_get_likes_errors_on_post_not_found(post_crud_setup: PostCrudSetup):
    s = post_crud_setup
    resp = await s.client.get('/users/me/posts/1/likes', headers=s.headers)
    assert resp.status_code == 404


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


@pytest.mark.asyncio
async def test_unliking_post_is_idempotent(liked_by_both: PostInteractionSetup):
    s = liked_by_both
    resp = await s.client.delete(_like_url(s), headers=s.user_auth)
    assert resp.status_code == 204
    resp = await s.client.delete(_like_url(s), headers=s.user_auth)
    assert resp.status_code == 204
    resp = await s.client.get(_post_url(s), headers=s.author_auth)

    assert resp.status_code == 200
    assert Post.model_validate(resp.json()).like_cnt == 1


@pytest.mark.asyncio
async def test_blocked_user_cannot_see_posts(
        alice_blocked_annoying: FollowingSetup,
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]],
        solid_black: bytes
):
    s = alice_blocked_annoying
    post = await post_factory(s.alice.user_id, solid_black, 'A nice pixel')
    resp = await s.client.get(f'/users/{s.alice.user_id}/posts/{post.post_id}', headers=s.alice_headers)
    assert resp.status_code == 200
    resp = await s.client.get(f'/users/{s.alice.user_id}/posts/{post.post_id}', headers=s.annoying_headers)
    assert resp.status_code == 403
