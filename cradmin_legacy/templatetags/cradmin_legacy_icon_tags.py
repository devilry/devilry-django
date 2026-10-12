from django import template
import logging

from django.conf import settings

from django.template.defaultfilters import stringfilter

from cradmin_legacy import css_icon_map

register = template.Library()
log = logging.getLogger(__name__)


@register.simple_tag
@stringfilter
def cradmin_icon(iconkey):
    """
    Returns the css class for an icon configured with the
    given key in ``CRADMIN_LEGACY_CSS_ICON_MAP``.
    """
    iconmap = getattr(settings, "CRADMIN_LEGACY_CSS_ICON_MAP", css_icon_map.FONT_AWESOME)
    icon_classes = iconmap.get(iconkey, "")
    if not icon_classes:
        log.warn('No icon named "%s" in settings.CRADMIN_LEGACY_ICONMAP.', iconkey)
    return icon_classes
