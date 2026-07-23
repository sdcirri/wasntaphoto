import pytest

from exceptions import BadImageError
from service.image_utils import upload2jpeg

from .conftest import rmsdiff


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


def test_image_utils_post_format_quality(any_image: bytes):
    post_format = upload2jpeg(any_image, 90, 720)
    assert rmsdiff(any_image, post_format) < 6


def test_image_utils_propic_format_quality(any_image: bytes):
    propic_format = upload2jpeg(any_image, 85, 480)
    assert rmsdiff(any_image, propic_format) < 10


def test_image_utils_raises_on_bad_image():
    img = b'\01\02\03'
    with pytest.raises(BadImageError):
        upload2jpeg(img, 90)
