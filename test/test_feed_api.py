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
