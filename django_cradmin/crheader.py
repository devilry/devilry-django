from django.conf import settings
from django.utils.module_loading import import_string

from django_cradmin import renderable


def get_default_header_renderable(**kwargs):
    """
    Get the default header renderable.

    The one set in the :setting:`DJANGO_CRADMIN_DEFAULT_HEADER_CLASS`.

    Args:
        **kwargs: Kwargs for the header class constructor.

    Returns:
        AbstractHeaderRenderable: Header renderable object or ``None``.
    """
    if not getattr(settings, "DJANGO_CRADMIN_DEFAULT_HEADER_CLASS", None):
        return None
    header_class = import_string(settings.DJANGO_CRADMIN_DEFAULT_HEADER_CLASS)
    return header_class(**kwargs)


class AbstractHeaderRenderable(renderable.AbstractRenderableWithCss):
    """
    Abstract base class for headers.

    You will typically want to use/extend :class:`.DefaultHeaderRenderable`
    instead of this unless you have some special needs.
    """

    def __init__(self, cradmin_instance=None, request=None):
        """

        Args:
            cradmin_instance (django_cradmin.crinstance.BaseCrAdminInstance): A
                cradmin instance object or ``None``.
            request: Not needed if you provide cradmin_instance.
        """
        self.cradmin_instance = cradmin_instance
        self.request = request
        if not request and cradmin_instance:
            self.request = cradmin_instance.request

    def get_wrapper_htmltag(self):
        """
        Get the HTML tag to wrap the header in.

        Defaults to ``"header"``.
        """
        return "header"

    def get_wrapper_htmltag_id(self):
        """
        Get the ID of the wrapper html tag.
        """
        return "id_django_cradmin_page_header"


class DefaultHeaderRenderable(AbstractHeaderRenderable):
    """
    The default header renderable class.
    """

    template_name = "django_cradmin/crheader/default-header.django.html"

    @property
    def bem_block(self):
        return "adminui-page-header"

    @property
    def bem_variants_list(self):
        """
        Get a list of BEM variants.

        These are added to the CSS classes prefixed with :meth:`bem_block`
        followed by ``--`` (``<bem_block>--<variant>``).
        """
        return []

    def expand_bem_variants_list(self):
        bem_block = self.bem_block
        return ["{}--{}".format(bem_block, variant) for variant in self.bem_variants_list]

    def get_base_css_classes_list(self):
        return [self.bem_block] + self.expand_bem_variants_list()

    def get_main_menu_renderable(self):
        """
        Get the main menu renderable.

        Returns :meth:`django_cradmin.crinstance.BaseCrAdminInstance.main_menu_renderable`
        if we have a ``cradmin_instance``, otherwise this returns ``None``.

        You can safely override this, and you will typically want to
        do so if you use the :setting:`DJANGO_CRADMIN_DEFAULT_HEADER_CLASS`.
        """
        if self.cradmin_instance:
            return self.cradmin_instance.main_menu_renderable
        return None
