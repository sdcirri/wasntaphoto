from PIL import Image, ImageChops
from io import BytesIO
import numpy as np
import os

os.environ['DATABASE_URL'] = 'postgresql+psycopg://'
os.environ['REDIS_URL'] = 'redis://fake:6379/0'
os.environ['MINIO_URL'] = 'localhost:9000'
os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
os.environ['MINIO_SECRET_KEY'] = 'minioadmin'

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
