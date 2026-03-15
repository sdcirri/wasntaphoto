from PIL import Image, UnidentifiedImageError
from io import BytesIO
import aiofiles.os
import aiofiles
import os

from exceptions import BadImageError


STORAGE_ROOT = os.getenv('WASA_STORAGE_ROOT', '/tmp')
POST_STORAGE_ROOT = os.path.join(STORAGE_ROOT, 'posts/')
PROPIC_STORAGE_ROOT = os.path.join(STORAGE_ROOT, 'propics/')
DEFAULT_PROPIC = os.path.join(STORAGE_ROOT, 'propics/default.jpg')
os.makedirs(POST_STORAGE_ROOT, exist_ok=True)
os.makedirs(PROPIC_STORAGE_ROOT, exist_ok=True)


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
        async with aiofiles.open(DEFAULT_PROPIC, 'rb') as f:
            return await f.read()


async def get_post_bytes(post_id: int) -> bytes:
    """
    Gets the post attached image.
    :param post_id: post ID
    :return: the post image bytes
    """
    try:
        async with aiofiles.open(os.path.join(POST_STORAGE_ROOT, f'{post_id}.jpg'), 'rb') as f:
            return await f.read()
    except FileNotFoundError:
        raise RuntimeError('Post has no attached image!')


def scale(img: Image.Image, target_height: int) -> Image.Image:
    """
    Scales an image to fit the target height, be it an upscale or
    a downscale
    :param img: image
    :param target_height: target height
    :return: the scaled image
    """
    w, h = img.size
    ratio = target_height / h
    return img.resize((int(w * ratio), target_height), Image.Resampling.LANCZOS)


def upload2jpeg(uploaded_image: bytes, quality: int, target_height: int | None = None) -> bytes:
    """
    Converts the uploaded image to a JPEG for storage
    :param uploaded_image: uploaded image
    :param quality: JPEG quality
    :param target_height: target height for scaling (None for no scaling)
    :return: the JPEG bytes
    """
    with BytesIO() as buf:
        try:
            img = Image.open(BytesIO(uploaded_image)).convert('RGB')
            if target_height:
                img = scale(img, target_height)
            img.save(buf, format='JPEG', quality=quality)
            return buf.getvalue()
        except (UnidentifiedImageError, OSError):
            raise BadImageError


async def upload2propic(user_id: int, uploaded_image: bytes) -> bytes:
    """
    Converts the uploaded image to propic format (JPEG at 85% quality)
    and saves it to disk
    :param user_id: user ID of the user who wants to set the propic
    :param uploaded_image: uploaded image
    :return: the JPEG bytes
    """
    propic = upload2jpeg(uploaded_image, 85, 480)
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
    post = upload2jpeg(uploaded_image, 90, 720)
    async with aiofiles.open(os.path.join(POST_STORAGE_ROOT, f'{post_id}.jpg'), 'wb') as f:
        await f.write(post)
    return post


async def delete_old_post(post_id: int) -> None:
    """
    Deletes an orphaned image
    :param post_id: deleted post
    """
    await aiofiles.os.remove(os.path.join(POST_STORAGE_ROOT, f'{post_id}.jpg'))
