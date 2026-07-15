import pytest

from model import Comment

from .fixtures.comments import CommentSetup


def _like_url(s: CommentSetup) -> str:
    return f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{s.comment.comment_id}/like'


def _bad_like_url(s: CommentSetup, bad_id: int) -> str:
    return f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{bad_id}/like'


def _comment_url(s: CommentSetup) -> str:
    return f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{s.comment.comment_id}'


@pytest.mark.asyncio
async def test_create_comment_returns_expected_fields(comment_setup: CommentSetup):
    s = comment_setup
    resp = await s.client.post(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/',
        headers=s.comment_author_headers,
        json='Very cool'
    )

    assert resp.status_code == 200
    comment = Comment.model_validate(resp.json())
    assert comment.author_id == s.comment_author.user_id
    assert comment.like_cnt == 0
    assert comment.content == 'Very cool'


@pytest.mark.asyncio
async def test_new_comment_appears_on_post(comment_setup: CommentSetup, existing_comment: Comment):
    s = comment_setup
    resp = await s.client.get(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}',
        headers=s.comment_author_headers
    )

    assert resp.status_code == 200
    assert resp.json()['comments'] == [existing_comment.comment_id]


@pytest.mark.asyncio
async def test_get_comment_by_id_returns_created_comment(comment_setup: CommentSetup, existing_comment: Comment):
    s = comment_setup
    resp = await s.client.get(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{existing_comment.comment_id}',
        headers=s.comment_author_headers
    )

    assert resp.status_code == 200
    assert Comment.model_validate(resp.json()) == existing_comment


@pytest.mark.asyncio
async def test_get_comment_by_id_errors_on_bad_id(comment_setup: CommentSetup, next_unused_comment_id: int):
    s = comment_setup
    resp = await s.client.get(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{next_unused_comment_id}',
        headers=s.comment_author_headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_comment_removes_it_from_post(comment_setup: CommentSetup, existing_comment: Comment):
    s = comment_setup
    del_resp = await s.client.delete(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{existing_comment.comment_id}',
        headers=s.comment_author_headers
    )
    assert del_resp.status_code == 204

    post_resp = await s.client.get(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}',
        headers=s.comment_author_headers
    )
    assert post_resp.status_code == 200
    assert post_resp.json()['comments'] == []


@pytest.mark.asyncio
async def test_delete_comment_errors_on_bad_id(comment_setup: CommentSetup, next_unused_comment_id: int):
    s = comment_setup
    del_resp = await s.client.delete(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{next_unused_comment_id}',
        headers=s.comment_author_headers
    )
    assert del_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_comment_no_idor(comment_setup: CommentSetup, existing_comment: Comment):
    s = comment_setup
    del_resp = await s.client.delete(
        f'/users/{s.post_author.user_id}/posts/{s.post.post_id}/comments/{existing_comment.comment_id}',
        headers=s.post_author_headers
    )
    assert del_resp.status_code == 403


@pytest.mark.asyncio
async def test_comment_starts_unliked(comment_like_setup: CommentSetup):
    s = comment_like_setup
    resp = await s.client.get(_like_url(s), headers=s.comment_author_headers)

    assert resp.status_code == 200
    assert resp.json() is False


@pytest.mark.asyncio
async def test_is_comment_liked_errors_on_bad_id(comment_setup: CommentSetup, next_unused_comment_id: int):
    s = comment_setup
    del_resp = await s.client.get(_bad_like_url(s, next_unused_comment_id), headers=s.comment_author_headers)
    assert del_resp.status_code == 404


@pytest.mark.asyncio
async def test_liking_comment_sets_like_status(comment_like_setup: CommentSetup):
    s = comment_like_setup
    put_resp = await s.client.put(_like_url(s), headers=s.comment_author_headers)
    assert put_resp.status_code == 204

    get_resp = await s.client.get(_like_url(s), headers=s.comment_author_headers)
    assert get_resp.json() is True


@pytest.mark.asyncio
async def test_liking_comment_errors_on_bad_id(comment_setup: CommentSetup, next_unused_comment_id: int):
    s = comment_setup
    del_resp = await s.client.put(_bad_like_url(s, next_unused_comment_id), headers=s.comment_author_headers)
    assert del_resp.status_code == 404


@pytest.mark.asyncio
async def test_liking_comment_increments_like_count(comment_like_setup: CommentSetup):
    s = comment_like_setup
    await s.client.put(_like_url(s), headers=s.comment_author_headers)

    resp = await s.client.get(_comment_url(s), headers=s.comment_author_headers)
    assert resp.status_code == 200
    assert Comment.model_validate(resp.json()).like_cnt == 1


@pytest.mark.asyncio
async def test_unliking_comment_clears_like_status(comment_like_setup: CommentSetup):
    s = comment_like_setup
    await s.client.put(_like_url(s), headers=s.comment_author_headers)

    del_resp = await s.client.delete(_like_url(s), headers=s.comment_author_headers)
    assert del_resp.status_code == 204

    get_resp = await s.client.get(_like_url(s), headers=s.comment_author_headers)
    assert get_resp.json() is False


@pytest.mark.asyncio
async def test_unliking_comment_errors_on_bad_id(comment_setup: CommentSetup, next_unused_comment_id: int):
    s = comment_setup
    del_resp = await s.client.delete(_bad_like_url(s, next_unused_comment_id), headers=s.comment_author_headers)
    assert del_resp.status_code == 404


@pytest.mark.asyncio
async def test_unliking_comment_decrements_like_count(comment_like_setup: CommentSetup):
    s = comment_like_setup
    await s.client.put(_like_url(s), headers=s.comment_author_headers)
    await s.client.delete(_like_url(s), headers=s.comment_author_headers)

    resp = await s.client.get(_comment_url(s), headers=s.comment_author_headers)
    assert Comment.model_validate(resp.json()).like_cnt == 0
