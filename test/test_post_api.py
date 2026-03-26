import asyncio
from typing import Callable, Coroutine, Any
from model import PostRequest, Post
from httpx import AsyncClient
import base64
import pytest

from db.entities import UserModel, PostModel
from test.fixtures.db import post_factory


@pytest.mark.asyncio
async def test_post_api(
        client: AsyncClient,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
        solid_black: bytes
):
    user = await user_factory('alice', 'H@xx0r.2026')
    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    headers = {'Authorization': f'Bearer {login.json()}'}

    req = PostRequest(image=base64.b64encode(solid_black), caption='A nice pixel')
    post = await client.post('/users/me/posts/', json=req.model_dump(mode='json'), headers=headers)
    assert post.status_code == 200
    info = Post.model_validate(post.json())
    assert info.author_id == user.user_id
    assert info.caption == 'A nice pixel'
    assert info.image

    post2 = await client.get(f'/users/me/posts/{info.post_id}', headers=headers)
    assert post2.status_code == 200
    info2 = Post.model_validate(post2.json())
    assert info == info2

    del_ = await client.delete(f'/users/me/posts/{info.post_id}', headers=headers)
    assert del_.status_code == 204
    info3 = await client.get(f'/users/me/posts/{info.post_id}', headers=headers)
    assert info3.status_code == 404


@pytest.mark.asyncio
async def test_post_api_interactions(
        client: AsyncClient,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]],
        gradient_rgb: bytes
):
    author, user = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'H@xx0r.2026')
    )
    post = await post_factory(author.user_id, gradient_rgb, 'Cool colors')

    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    alice_auth = {'Authorization': f'Bearer {login.json()}'}
    login = await client.post('/session/', json={'username': 'bob', 'password': 'H@xx0r.2026'})
    bob_auth = {'Authorization': f'Bearer {login.json()}'}

    like = await client.put(f'/users/{author.user_id}/posts/{post.post_id}/like', headers=bob_auth)
    assert like.status_code == 204
    like2 = await client.put(f'/users/me/posts/{post.post_id}/like', headers=alice_auth)
    assert like2.status_code == 204

    post = await client.get(f'/users/me/posts/{post.post_id}', headers=alice_auth)
    post = Post.model_validate(post.json())
    assert post.like_cnt == 2

    likes = await client.get(f'/users/me/posts/{post.post_id}/likes', headers=alice_auth)
    assert likes.status_code == 200
    assert set(likes.json()) == {user.user_id, author.user_id}

    likes = await client.get(f'/users/me/posts/{post.post_id}/likes', headers=bob_auth)
    assert likes.status_code == 403

    unlike = await client.delete(f'/users/{author.user_id}/posts/{post.post_id}/like', headers=bob_auth)
    assert unlike.status_code == 204

    likes = await client.get(f'/users/me/posts/{post.post_id}/likes', headers=alice_auth)
    assert likes.status_code == 200
    assert set(likes.json()) == {author.user_id}
