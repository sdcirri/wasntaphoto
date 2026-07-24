from PIL import Image, UnidentifiedImageError
from io import BytesIO

from exceptions import BadImageError


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


def upload2jpeg(uploaded_image: bytes, quality: int, target_height: int) -> bytes:
    """
    Converts the uploaded image to a JPEG for storage
    :param uploaded_image: uploaded image
    :param quality: JPEG quality
    :param target_height: target height for scaling
    :return: the JPEG bytes
    """
    with BytesIO() as buf:
        try:
            img = Image.open(BytesIO(uploaded_image)).convert('RGB')
            img = scale(img, target_height)
            img.save(buf, format='JPEG', quality=quality)
            return buf.getvalue()
        except (UnidentifiedImageError, OSError):
            raise BadImageError


def upload2propic(uploaded_image: bytes) -> bytes:
    """
    Converts the uploaded image to propic format (JPEG at 85% quality)
    :param uploaded_image: uploaded image
    :return: the JPEG bytes
    """
    return upload2jpeg(uploaded_image, 85, 480)


def upload2post(uploaded_image: bytes) -> bytes:
    """
    Converts the uploaded image to post format (JPEG at 90% quality)
    and saves it to disk
    :param uploaded_image: uploaded image
    :return: the JPEG bytes
    """
    return upload2jpeg(uploaded_image, 90, 720)
