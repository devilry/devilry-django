from django import template
import logging

from django.conf import settings

from django.template.defaultfilters import stringfilter

from django_cradmin import css_icon_map

register = template.Library()
log = logging.getLogger(__name__)


@register.simple_tag
@stringfilter
def cradmin_icon(iconkey):
    """
    Returns the css class for an icon configured with the
    given key in ``DJANGO_CRADMIN_CSS_ICON_MAP``.
    """
    iconmap = getattr(settings, "DJANGO_CRADMIN_CSS_ICON_MAP", css_icon_map.FONT_AWESOME)
    icon_classes = iconmap.get(iconkey, "")
    if not icon_classes:
        log.warn('No icon named "%s" in settings.DJANGO_CRADMIN_ICONMAP.', iconkey)
    return icon_classes
