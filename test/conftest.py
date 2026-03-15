from PIL import Image
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
