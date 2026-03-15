from PIL import Image, ImageChops
from io import BytesIO
import numpy as np
import pytest

from service.image_utils import upload2jpeg


def rmsdiff(img1: bytes, img2: bytes) -> float:
    img1 = Image.open(BytesIO(img1)).convert('RGB')
    img2 = Image.open(BytesIO(img2)).convert('RGB').resize(img1.size)
    diff = ImageChops.difference(img1, img2)
    h = np.array(diff)
    return np.sqrt(np.mean(h**2))


ALL_IMAGE_FIXTURES = [
    'solid_red', 'solid_black', 'solid_white', 'solid_transparent',
    'gradient_horizontal', 'gradient_vertical', 'gradient_rgb', 'gradient_radial',
    'checkerboard', 'checkerboard_rgb',
    'stripes_horizontal', 'stripes_vertical',
    'single_pixel', 'non_square', 'odd_dimensions',
]


@pytest.fixture(params=ALL_IMAGE_FIXTURES)
def any_image(request) -> bytes:
    return request.getfixturevalue(request.param)


@pytest.mark.asyncio
def test_image_utils(any_image: bytes):
    post_format = upload2jpeg(any_image, 90, 720)
    assert rmsdiff(any_image, post_format) < 6
    propic_format = upload2jpeg(any_image, 85, 480)
    assert rmsdiff(any_image, propic_format) < 10
