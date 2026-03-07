from PIL import Image, UnidentifiedImageError
from io import BytesIO
import aiofiles
import os.path

from exceptions import BadImageError


POST_STORAGE_ROOT = 'posts/'
PROPIC_STORAGE_ROOT = 'propics/'
DEFAULT_PROPIC = 'propics/default.jpg'


async def get_propic_bytes(user_id: int) -> bytes:
    """
    Gets the user's propic. If not set, returns the default one
    :param user_id: user ID
    :return: the propic bytes
    """
    try:
        async with aiofiles.open(os.path.join(PROPIC_STORAGE_ROOT, f'{user_id}.jpg'), 'rb') as f:
            return await f.read()
    except FileNotFoundError:
        async with aiofiles.open(os.path.join(DEFAULT_PROPIC), 'rb') as f:
            return await f.read()


async def get_post_bytes(post_id: int) -> bytes:
    """
    Gets the post attached image.
    :param post_id: post ID
    :return: the propic bytes
    """
    try:
        async with aiofiles.open(os.path.join(PROPIC_STORAGE_ROOT, f'{post_id}.jpg'), 'rb') as f:
            return await f.read()
    except FileNotFoundError:
        raise RuntimeError('Post has no attached image!')


def upload2jpeg(uploaded_image: bytes, quality: int) -> bytes:
    """
    Converts the uploaded image to a JPEG for storage
    :param uploaded_image: uploaded image
    :param quality: JPEG quality
    :return: the JPEG bytes
    """
    with BytesIO() as buf:
        try:
            img = Image.open(BytesIO(uploaded_image))
            img.save(buf, format='JPEG', quality=quality)
            return buf.getvalue()
        except UnidentifiedImageError:
            raise BadImageError


async def upload2propic(user_id: int, uploaded_image: bytes) -> bytes:
    """
    Converts the uploaded image to propic format (JPEG at 85% quality)
    and saves it to disk
    :param user_id: user ID of the user who wants to set the propic
    :param uploaded_image: uploaded image
    :return: the JPEG bytes
    """
    propic = upload2jpeg(uploaded_image, 85)
    async with aiofiles.open(os.path.join(PROPIC_STORAGE_ROOT, f'{user_id}.jpg'), 'wb') as f:
        await f.write(propic)
    return propic


async def upload2post(post_id: int, uploaded_image: bytes) -> bytes:
    """
    Converts the uploaded image to post format (JPEG at 90% quality)
    and saves it to disk
    :param post_id: post ID
    :param uploaded_image: uploaded image
    :return: the JPEG bytes
    """
    post = upload2jpeg(uploaded_image, 90)
    async with aiofiles.open(os.path.join(POST_STORAGE_ROOT, f'{post_id}.jpg'), 'wb') as f:
        await f.write(post)
    return post
