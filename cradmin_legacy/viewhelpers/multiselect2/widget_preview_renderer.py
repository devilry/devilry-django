from cradmin_legacy.viewhelpers import listbuilder


class List(listbuilder.lists.RowList):
    """
    Renders a list for previewing selection in
    :class:`cradmin_legacy.viewhelpers.multiselect2.manytomanywidget.Widget`.
    """

    template_name = "cradmin_legacy/viewhelpers/multiselect2/manytomanywidget/preview-list.django.html"

    @classmethod
    def from_value_iterable(cls, value_iterable, value_renderer_class=None, frame_renderer_class=None, **listkwargs):
        """
        Overrides :meth:`.cradmin_legacy.viewhelpers.listbuilder.base.List.from_value_iterable`
        to set :class:`.Value` as the default ``value_renderer_class``.
        """
        if value_renderer_class is None:
            value_renderer_class = Value
        return super().from_value_iterable(
            value_iterable=value_iterable,
            value_renderer_class=value_renderer_class,
            frame_renderer_class=frame_renderer_class,
            **listkwargs,
        )

    def get_base_css_classes_list(self):
        """
        Adds the ``cradmin-legacy-multiselect2-preview-list`` css class
        to the css classes added by the superclasses.
        """
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-multiselect2-preview-list")
        return css_classes


class Value(listbuilder.base.ItemValueRenderer):
    """
    Renders a single value in :class:`.List` - also used
    by the ``get_manytomanyfield_preview_renderer_class`` method in
    :class:`~cradmin_legacy.viewhelpers.multiselect2.listbuilder_itemvalues.ManyToManySelect`
    """

    template_name = "cradmin_legacy/viewhelpers/multiselect2/manytomanywidget/preview-value.django.html"

    def __init__(self, value, wrap_in_li_element=False):
        """
        Args:
            value: See :class:`cradmin_legacy.viewhelpers.listbuilder.base.AbstractItemRenderer`.
            wrap_in_li_element: If this is set to ``True``, we wrap the rendered item in
                an ``<li>``.

                This is set to ``True`` by the ``get_manytomanyfield_preview_html``-method in
                :class:`cradmin_legacy.viewhelpers.multiselect2.listbuilder_itemvalues.ManyToManySelect`
                to render items that can be dynamically added to a :class:`.List`.
        """
        self.wrap_in_li_element = wrap_in_li_element
        super().__init__(value=value)

    def get_base_css_classes_list(self):
        """
        Adds the ``cradmin-legacy-multiselect2-preview-list-value`` css class
        to the css classes added by the superclasses.
        """
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-multiselect2-preview-list-value")
        return css_classes
