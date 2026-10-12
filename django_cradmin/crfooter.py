from django.conf import settings
from django.utils.module_loading import import_string

from django_cradmin import renderable


def get_default_footer_renderable(**kwargs):
    """
    Get the default footer renderable.

    The one set in the :setting:`DJANGO_CRADMIN_DEFAULT_FOOTER_CLASS`.

    Args:
        **kwargs: Kwargs for the footer class constructor.

    Returns:
        AbstractFooter: Header renderable object or ``None``.
    """
    if not getattr(settings, "DJANGO_CRADMIN_DEFAULT_FOOTER_CLASS", None):
        return None
    footer_class = import_string(settings.DJANGO_CRADMIN_DEFAULT_FOOTER_CLASS)
    return footer_class(**kwargs)


class AbstractFooter(renderable.AbstractRenderableWithCss):
    def __init__(self, cradmin_instance=None, request=None):
        self.cradmin_instance = cradmin_instance
        self.request = request
        if not request and cradmin_instance:
            self.request = cradmin_instance.request

    def get_wrapper_htmltag(self):
        """
        Get the HTML tag to wrap the footer in.

        Defaults to ``"footer"``.
        """
        return "footer"
