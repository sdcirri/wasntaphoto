import pytest

from .fixtures.posts import PostInteractionSetup


@pytest.mark.asyncio
async def test_user_feed_contains_posts_from_followed(post_interaction_setup: PostInteractionSetup):
    s = post_interaction_setup
    await s.client.post(f'/users/me/following/{s.author.user_id}', headers=s.user_auth)
    resp = await s.client.get('/feed/', headers=s.user_auth)
    assert resp.status_code == 200
    feed = resp.json()
    assert len(feed) == 1
    assert feed[0] == s.post.post_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'bad_request_path',
    ['/feed/?n=-1&p=0', '/feed/?n=0&p=0', '/feed/?n=101&p=0', '/feed/?n=10&p=-1']
)
async def test_get_user_feed_rejects_invalid_requests(
        post_interaction_setup: PostInteractionSetup,
        bad_request_path: str
):
    s = post_interaction_setup
    resp = await s.client.get(bad_request_path, headers=s.user_auth)
    assert resp.status_code == 422
