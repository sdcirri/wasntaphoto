from model import PostRequest, Post
from io import BytesIO
from PIL import Image
import base64
import pytest


@pytest.mark.asyncio
async def test_post_api(client, user_factory):
    user = await user_factory('alice', 'H@xx0r.2026')
    login = await client.post('/session/', json={'username': 'alice', 'password': 'H@xx0r.2026'})
    headers = {'Authorization': f'Bearer {login.json()}'}

    with BytesIO() as b:
        Image.new('RGB', (1, 1), (255, 0, 0)).save(b, format='JPEG')
        img = b.getvalue()

    req = PostRequest(image=base64.b64encode(img), caption='A nice pixel')
    post_id = await client.post('/users/me/posts/', json=req.model_dump(mode='json'), headers=headers)
    assert post_id.status_code == 200
    assert Post.model_validate(post_id.json()).post_id == 1

    info = await client.get('/users/me/posts/', headers=headers)
    assert info.status_code == 200
    assert len(info.json()) == 1
    info = Post.model_validate(info.json()[0])
    assert info.post_id == 1
    assert info.author_id == user.user_id
    assert info.caption == 'A nice pixel'
    assert info.image
