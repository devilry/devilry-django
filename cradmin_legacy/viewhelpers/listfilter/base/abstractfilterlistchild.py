from cradmin_legacy.renderable import AbstractRenderableWithCss


class FilterListChildMixin:
    """
    Mixin class for adding the methods in addition to
    the methods in :class:`cradmin_legacy.renderable.AbstractRenderableWithCss`
    required to be added as a child of
    :class:`~cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList`.

    You can use this if you have an existing AbstractRenderableWithCss
    that you want to add to an AbstractFilterList. This means that you
    can make renderables that can be used both in a filterlist and
    on its own.
    """

    def set_filterlist(self, filterlist):
        """
        Set ``self.filterlist = filterlist``.

        This method is called by
        :class:`~cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList.append`
        to give the child a way to access the filterlist.
        """
        self.filterlist = filterlist


class AbstractFilterListChild(AbstractRenderableWithCss, FilterListChildMixin):
    """
    Base class for anything that can be added as a child of
    :class:`~cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist.AbstractFilterList`.
    """

    def __init__(self):
        self.filterlist = None
