from io import BytesIO

from PIL import Image, ImageDraw


def create_image(width, height, filetype="PNG"):
    """
    Create an image of the given ``width``, ``height`` and optional ``filetype``.

    Returns:
        A bytestring with the generated image.
    """
    im = Image.new("RGB", (width, height), color="#191919")
    ImageDraw.Draw(im)
    out = BytesIO()
    im.save(out, filetype)
    return out.getvalue()
