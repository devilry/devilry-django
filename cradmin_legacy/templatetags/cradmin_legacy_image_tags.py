from django.template import Library
from cradmin_legacy import imageutils
import logging
from cradmin_legacy.imageutils.backends.backendinterface import ImageTypeMapSettingNotDefined, InvalidImageType

register = Library()
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def cradmin_transform_image(context, imageurl, **options):
    """
    Tag wrapper around
    :meth:`~cradmin_legacy.imageutils.backends.backendinterface.Interface.transform_image`.

    Parameters:

        imageurl: The URL of the image to transform.
        options: Image transformation options.
    """
    request = context["request"]
    imageurl = request.build_absolute_uri(imageurl)
    if "options" in options:
        options = options["options"]
    return imageutils.get_backend().transform_image(imageurl, **options)


@register.simple_tag(takes_context=True)
def cradmin_transform_image_using_imagetype(context, imageurl, imagetype, fallbackoptions=None):
    """
    Tag wrapper around
    :meth:`~cradmin_legacy.imageutils.backends.backendinterface.Interface.transform_image_using_imagetype`.

    Parameters:

        imageurl: The URL of the image to transform.
        imagetype: See
            :meth:`~cradmin_legacy.imageutils.backends.backendinterface.Interface.transform_image_using_imagetype`.
        fallbackoptions: An optional dict of options to use if ``imagetype``
            is not in the :setting:`CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP` setting.
    """
    request = context["request"]
    imageurl = request.build_absolute_uri(imageurl)
    try:
        return imageutils.get_backend().transform_image_using_imagetype(imageurl, imagetype)
    except (ImageTypeMapSettingNotDefined, InvalidImageType):
        if fallbackoptions:
            return imageutils.get_backend().transform_image(imageurl, **fallbackoptions)
        else:
            raise


@register.inclusion_tag("cradmin_legacy/imageutils/templatetags/archiveimage-tag.django.html", takes_context=True)
def cradmin_create_archiveimage_tag(context, archiveimage, imagetype, css_class="", fallbackoptions=None):
    """
    Creates an ``<img>`` tag from the given cradmin archiveimage.

    The URL is generated using
    :meth:`.cradmin_transform_image_using_imagetype`.

    The alt-tag is generated from ``archiveimage.screenreader_text``.
    """
    return {
        "archiveimage": archiveimage,
        "url": cradmin_transform_image_using_imagetype(
            context=context, imageurl=archiveimage.image.url, imagetype=imagetype, fallbackoptions=fallbackoptions
        ),
        "css_class": css_class,
    }
