from typing import Callable, Coroutine, Any
from httpx import AsyncClient
import asyncio
import pytest

from db.entities import UserModel, PostModel, CommentModel
from model import Comment


@pytest.mark.asyncio
async def test_comment_api(
        client: AsyncClient,
        gradient_rgb: bytes,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]]
):
    post_author, comment_author = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'H@xx0r.2026')
    )
    post = await post_factory(post_author.user_id, gradient_rgb, 'Cool colors')

    login = await client.post('/session/', json={'username': 'bob', 'password': 'H@xx0r.2026'})
    comment_author_auth = {'Authorization': f'Bearer {login.json()}'}

    comment_req = await client.post(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/',
        headers=comment_author_auth,
        json='Very cool'
    )
    assert comment_req.status_code == 200
    comment = Comment.model_validate(comment_req.json())
    assert comment.author_id == comment_author.user_id
    assert comment.like_cnt == 0
    assert comment.content == 'Very cool'

    post_req = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}',
        headers=comment_author_auth
    )
    assert post_req.status_code == 200
    assert len(post_req.json()['comments']) == 1
    assert post_req.json()['comments'][0] == comment.comment_id

    comment_req = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}',
        headers=comment_author_auth
    )
    assert comment_req.status_code == 200
    assert Comment.model_validate(comment_req.json()) == comment

    del_req = await client.delete(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}',
        headers=comment_author_auth
    )
    assert del_req.status_code == 204

    post_req2 = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}',
        headers=comment_author_auth
    )
    assert post_req2.status_code == 200
    assert len(post_req2.json()['comments']) == 0


@pytest.mark.asyncio
async def test_comment_interaction_api(
        client: AsyncClient,
        gradient_rgb: bytes,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]],
        comment_factory: Callable[[int, int, str], Coroutine[Any, Any, CommentModel]]
):
    post_author, comment_author = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'H@xx0r.2026')
    )
    post = await post_factory(post_author.user_id, gradient_rgb, 'Cool colors')
    comment = await comment_factory(comment_author.user_id, post.post_id, 'Very cool')

    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    post_author_auth = {'Authorization': f'Bearer {login.json()}'}

    like = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}/like',
        headers=post_author_auth
    )
    assert like.status_code == 200
    assert like.json() == False

    like = await client.put(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}/like',
        headers=post_author_auth
    )
    assert like.status_code == 204
    like = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}/like',
        headers=post_author_auth
    )
    assert like.json() == True

    comment_req = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}',
        headers=post_author_auth
    )
    assert comment_req.status_code == 200
    assert Comment.model_validate(comment_req.json()).like_cnt == 1

    unlike = await client.delete(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}/like',
        headers=post_author_auth
    )
    assert unlike.status_code == 204
    like = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}/like',
        headers=post_author_auth
    )
    assert like.json() == False
    comment_req = await client.get(
        f'/users/{post_author.user_id}/posts/{post.post_id}/comments/{comment.comment_id}',
        headers=post_author_auth
    )
    assert Comment.model_validate(comment_req.json()).like_cnt == 0
