from cradmin_legacy.viewhelpers.listbuilder import base


class DefaultSpacingItemFrame(base.ItemFrameRenderer):
    """
    Renders a frame that adds some spacing around the items in the list.
    """

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-itemframe-defaultspacing")
        return css_classes


class Link(DefaultSpacingItemFrame):
    """
    Renders a frame as a link.
    """

    template_name = "cradmin_legacy/viewhelpers/listbuilder/itemframe/link.django.html"

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-itemframe-link")
        return css_classes

    def get_url(self):
        """
        Get the URL the link should go to.

        Defaults to ``value.get_absolute_url``, which means that this
        works out of the box with any Django model object with
        the ``get_absolute_url`` method defined.
        """
        return self.value.get_absolute_url()
