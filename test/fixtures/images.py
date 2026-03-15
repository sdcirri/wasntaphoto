from io import BytesIO
from PIL import Image
import numpy as np
import pytest


def _img(arr: np.ndarray, output_format: str = 'PNG', mode: str = 'RGB') -> bytes:
    with BytesIO() as buf:
        Image.fromarray(arr.astype(np.uint8), mode).save(buf, format=output_format)
        return buf.getvalue()


@pytest.fixture
def solid_red() -> bytes:
    return _img(np.full((100, 100, 3), [255, 0, 0]))


@pytest.fixture
def solid_black() -> bytes:
    return _img(np.zeros((100, 100, 3)))


@pytest.fixture
def solid_white() -> bytes:
    return _img(np.full((100, 100, 3), 255))


@pytest.fixture
def solid_transparent() -> bytes:
    arr = np.zeros((100, 100, 4), dtype=np.uint8)
    return _img(arr, mode='RGBA')


@pytest.fixture
def gradient_horizontal() -> bytes:
    arr = np.tile(np.linspace(0, 255, 100, dtype=np.uint8), (100, 1))
    return _img(arr, mode='L')


@pytest.fixture
def gradient_vertical() -> bytes:
    arr = np.tile(np.linspace(0, 255, 100, dtype=np.uint8), (100, 1)).T
    return _img(arr, mode='L')


@pytest.fixture
def gradient_rgb() -> bytes:
    h, w = 100, 100
    r = np.tile(np.linspace(0, 255, w, dtype=np.uint8), (h, 1))
    g = np.tile(np.linspace(0, 255, h, dtype=np.uint8), (w, 1)).T
    b = np.full((h, w), 128, dtype=np.uint8)
    return _img(np.dstack([r, g, b]))


@pytest.fixture
def gradient_radial() -> bytes:
    h, w = 100, 100
    cy, cx = h / 2, w / 2
    y, x = np.ogrid[:h, :w]
    dist = np.hypot(x - cx, y - cy)
    arr = np.clip(255 * (1 - dist / dist.max()), 0, 255).astype(np.uint8)
    return _img(arr, mode='L')


@pytest.fixture
def checkerboard() -> bytes:
    tile = np.kron(
        np.indices((10, 10)).sum(axis=0) % 2,
        np.ones((10, 10), dtype=np.uint8),
    ) * 255
    return _img(tile, mode='L')


@pytest.fixture
def checkerboard_rgb() -> bytes:
    tile_bw = np.kron(
        np.indices((10, 10)).sum(axis=0) % 2,
        np.ones((10, 10), dtype=np.uint8),
    )
    r = tile_bw * 255
    g = np.zeros_like(r)
    b = (1 - tile_bw) * 255
    return _img(np.dstack([r, g, b]))


@pytest.fixture
def stripes_horizontal() -> bytes:
    row = np.zeros(100, dtype=np.uint8)
    row[::20] = 255
    arr = np.repeat(
        (np.arange(100) // 10 % 2 * 255).astype(np.uint8)[:, None],
        100, axis=1,
    )
    return _img(arr, mode='L')


@pytest.fixture
def stripes_vertical() -> bytes:
    arr = np.repeat(
        (np.arange(100) // 10 % 2 * 255).astype(np.uint8)[None, :],
        100, axis=0,
    )
    return _img(arr, mode='L')


@pytest.fixture
def single_pixel() -> bytes:
    return _img(np.array([[[128, 64, 32]]], dtype=np.uint8))


@pytest.fixture
def non_square() -> bytes:
    return _img(np.full((90, 160, 3), [0, 128, 255]))


@pytest.fixture
def odd_dimensions() -> bytes:
    return _img(np.full((99, 101, 3), [200, 100, 50]))
