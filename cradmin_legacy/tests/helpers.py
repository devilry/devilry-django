import unittest
from io import BytesIO

from django.contrib.auth import get_user_model

try:
    from PIL import Image, ImageDraw
except ImportError:  # Pillow is optional - tests that need images are skipped without it.
    Image = ImageDraw = None


def create_user(username=None, password="test", **kwargs):
    """
    Create a user with the given ``username``.

    .. deprecated:: 1.0.1b8
        Use model_bakery instead.
    """
    user = get_user_model().objects.create(username=username, **kwargs)
    user.set_password(password)
    user.save()
    return user


def create_image(width, height, filetype="PNG"):
    """
    Create an image of the given ``width``, ``height`` and optional ``filetype``.

    Skips the calling test if Pillow is not installed.

    Returns:
        A bytestring with the generated image.
    """
    if Image is None:
        raise unittest.SkipTest("Pillow is not installed")
    im = Image.new("RGB", (width, height), color="#191919")
    ImageDraw.Draw(im)
    out = BytesIO()
    im.save(out, filetype)
    return out.getvalue()
