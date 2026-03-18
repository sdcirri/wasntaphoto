from PIL import Image, ImageChops
from io import BytesIO
import numpy as np
import os

os.environ['DATABASE_URL'] = 'postgresql+psycopg://'
os.environ['WASA_STORAGE_ROOT'] = '/tmp/wasa'
os.makedirs(os.environ['WASA_STORAGE_ROOT'], exist_ok=True)

pytest_plugins = (
    'test.fixtures.images',
    'test.fixtures.http',
    'test.fixtures.db',
)

from service.image_utils import DEFAULT_PROPIC


with open(DEFAULT_PROPIC, 'wb') as f:
    # One pixel JPEG
    Image.new('RGB', (1, 1), (255, 0, 0)).save(f, format="JPEG")


def rmsdiff(img1: bytes, img2: bytes) -> float:
    img1 = Image.open(BytesIO(img1)).convert('RGB')
    img2 = Image.open(BytesIO(img2)).convert('RGB').resize(img1.size)
    diff = ImageChops.difference(img1, img2)
    h = np.array(diff)
    return np.sqrt(np.mean(h**2))
