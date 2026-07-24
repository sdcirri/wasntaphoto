from PIL import Image, ImageChops
from io import BytesIO
import numpy as np
import os

os.environ['DATABASE_URL'] = 'postgresql+psycopg://'

pytest_plugins = (
    'test.fixtures.images',
    'test.fixtures.http',
    'test.fixtures.db',
    'test.fixtures.comments',
    'test.fixtures.users',
    'test.fixtures.posts',
    'test.fixtures.redis',
    'test.fixtures.services',
    'test.fixtures.minio',
)


def rmsdiff(img1: bytes, img2: bytes) -> float:
    img1 = Image.open(BytesIO(img1)).convert('RGB')
    img2 = Image.open(BytesIO(img2)).convert('RGB').resize(img1.size)
    diff = ImageChops.difference(img1, img2)
    h = np.array(diff)
    return np.sqrt(np.mean(h**2))
