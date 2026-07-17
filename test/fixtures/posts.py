from typing import Callable, Coroutine, Any
from types import SimpleNamespace
from httpx import AsyncClient
import pytest_asyncio
import asyncio
import base64

from db.entities import UserModel, PostModel
from model import PostRequest, Post



class PostCrudSetup(SimpleNamespace):
    client: AsyncClient
    user: UserModel
    headers: dict[str, str]


class PostInteractionSetup(SimpleNamespace):
    client: AsyncClient
    post: PostModel
    author: UserModel
    user: UserModel
    author_auth: dict[str, str]
    user_auth: dict[str, str]


def like_url(s: PostInteractionSetup) -> str:
    return f'/users/{s.author.user_id}/posts/{s.post.post_id}/like'


def likes_url(s: PostInteractionSetup) -> str:
    return f'/users/me/posts/{s.post.post_id}/likes'


def post_url(s: PostInteractionSetup) -> str:
    return f'/users/me/posts/{s.post.post_id}'


@pytest_asyncio.fixture
async def post_crud_setup(
        client: AsyncClient,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
) -> PostCrudSetup:
    """
    Registers and logs in a single user with no posts yet.
    """

    user = await user_factory('alice', 'H@xx0r.2026')
    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    headers = {'Authorization': f'Bearer {login.json()}'}
    return PostCrudSetup(client=client, user=user, headers=headers)


@pytest_asyncio.fixture
async def post_interaction_setup(
        client: AsyncClient,
        user_factory: Callable[[str, str], Coroutine[Any, Any, UserModel]],
        post_factory: Callable[[int, bytes, str], Coroutine[Any, Any, PostModel]],
        gradient_rgb: bytes
) -> PostInteractionSetup:
    """
    Creates a post by one user and logs in both that author and a
    second, unrelated user.
    """

    author, user = await asyncio.gather(
        user_factory('alice', 'H@xx0r.2026'),
        user_factory('bob', 'H@xx0r.2026')
    )
    post = await post_factory(author.user_id, gradient_rgb, 'Cool colors')

    author_login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    author_auth = {'Authorization': f'Bearer {author_login.json()}'}
    user_login = await client.post('/session/', json={'username': 'bob', 'password': 'H@xx0r.2026'})
    user_auth = {'Authorization': f'Bearer {user_login.json()}'}

    return PostInteractionSetup(
        client=client, post=post, author=author, user=user,
        author_auth=author_auth, user_auth=user_auth,
    )


@pytest_asyncio.fixture
async def created_post(post_crud_setup: PostCrudSetup, solid_black: bytes) -> Post:
    """
    Builds on post_crud_setup by creating a post via the API, for tests
    that need a post to already exist.
    """

    s = post_crud_setup
    req = PostRequest(image=base64.b64encode(solid_black), caption='A nice pixel')
    resp = await s.client.post('/users/me/posts/', json=req.model_dump(mode='json'), headers=s.headers)
    assert resp.status_code == 200
    return Post.model_validate(resp.json())


@pytest_asyncio.fixture
async def liked_by_both(post_interaction_setup: PostInteractionSetup) -> PostInteractionSetup:
    """
    Builds on post_interaction_setup with both the author and the other
    user having liked the post already.
    """

    s = post_interaction_setup
    resp = await s.client.put(like_url(s), headers=s.user_auth)
    assert resp.status_code == 204
    resp = await s.client.put(like_url(s), headers=s.author_auth)
    assert resp.status_code == 204
    return s
