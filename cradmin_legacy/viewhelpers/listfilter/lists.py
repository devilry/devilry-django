from cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist import AbstractFilterList


class Vertical(AbstractFilterList):
    """
    An :class:`~cradmin_legacy.viewhelpers.listfilter.base.AbstractFilterList`
    with css class optimized for vertical rendering.
    """

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listfilter-filterlist-vertical")
        return css_classes


class Horizontal(AbstractFilterList):
    """
    An :class:`~cradmin_legacy.viewhelpers.listfilter.base.AbstractFilterList`
    with css class optimized for horizontal rendering.
    """

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listfilter-filterlist-horizontal")
        return css_classes
