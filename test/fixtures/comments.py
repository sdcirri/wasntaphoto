from typing import Callable, Coroutine, Any
from types import SimpleNamespace

from httpx import AsyncClient
import pytest_asyncio
import asyncio

from db.entities import UserModel, PostModel, CommentModel
from model import Comment


class CommentSetup(SimpleNamespace):
    client: AsyncClient
    post: PostModel
    post_author: UserModel
    comment: CommentModel
    post_author_headers: dict[str, str]
    comment_author_headers: dict[str, str]


@pytest_asyncio.fixture
async def comment_setup(
        client: AsyncClient,
        gradient_rgb: bytes,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]]
) -> CommentSetup:
    """
    Creates a post by one user, logs in a second user, and returns
    everything needed to comment on that post.
    """

    post_author, comment_author = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'H@xx0r.2026'),
    )
    post = await post_factory(post_author.user_id, gradient_rgb, 'Cool colors')
    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    post_author_headers = {'Authorization': f'Bearer {login.json()}'}
    login = await client.post('/session/', json={'username': 'bob', 'password': 'H@xx0r.2026'})
    comment_author_headers = {'Authorization': f'Bearer {login.json()}'}
    return CommentSetup(
        client=client,
        post=post,
        post_author=post_author,
        comment_author=comment_author,
        post_author_headers=post_author_headers,
        comment_author_headers=comment_author_headers,
    )


@pytest_asyncio.fixture
async def comment_like_setup(
        client: AsyncClient,
        gradient_rgb: bytes,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]],
        comment_factory: Callable[[int, int, str], Coroutine[Any, Any, CommentModel]]
) -> CommentSetup:
    """
    Creates a post with an existing comment, and logs in the post author
    (who will be doing the liking/unliking).
    """

    post_author, comment_author = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'H@xx0r.2026')
    )
    post = await post_factory(post_author.user_id, gradient_rgb, 'Cool colors')
    comment = await comment_factory(comment_author.user_id, post.post_id, 'Very cool')
    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    post_author_headers = {'Authorization': f'Bearer {login.json()}'}
    login = await client.post('/session/', json={'username': 'bob', 'password': 'H@xx0r.2026'})
    comment_author_headers = {'Authorization': f'Bearer {login.json()}'}
    return CommentSetup(
        client=client,
        post=post,
        post_author=post_author,
        comment=comment,
        post_author_headers=post_author_headers,
        comment_author_headers=comment_author_headers,
    )


@pytest_asyncio.fixture
async def existing_comment(comment_setup: CommentSetup) -> Comment:
    """
    Builds on comment_setup by actually creating a comment via the API,
    for tests that need a comment to already exist.
    """

    s = comment_setup
    resp = await s.client.post(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/',
        headers=s.comment_author_headers,
        json='Very cool'
    )
    assert resp.status_code == 200
    return Comment.model_validate(resp.json())
