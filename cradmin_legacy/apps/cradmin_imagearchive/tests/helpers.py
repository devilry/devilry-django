import unittest
from io import BytesIO

try:
    from PIL import Image, ImageDraw
except ImportError:  # Pillow is optional - tests that need images are skipped without it.
    Image = ImageDraw = None


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
