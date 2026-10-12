import json
from xml.sax.saxutils import quoteattr

from django.utils.translation import pgettext_lazy

from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.viewhelpers.multiselect2 import selected_item_renderer
from cradmin_legacy.viewhelpers.multiselect2 import target_renderer
from cradmin_legacy.viewhelpers.multiselect2 import widget_preview_renderer


class ItemValue(listbuilder.itemvalue.TitleDescription):
    """
    Listbuilder itemvalue renderable that renders some information
    and a "Select" buttonn that works out of the box with
    :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`
    to enable multiselect.

    If you have multiple lists with multiselect2 on the same page,
    you have to ensure the DOM IDs are unique by overriding:

    - :meth:`~.ItemValue.get_selectbutton_dom_id`.
    - :meth:`~.ItemValue.get_target_dom_id` (or use the ``target_dom_id`` parameter). Make sure you
      set :meth:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target.get_target_dom_id`
      on your corresponding Target renderer to reflect the new ID.
    - :meth:`cradmin_legacy.viewhelpers.multiselect2.selected_item_renderer.SelectedItem.get_inputfield_name`
      of the :meth:`~.ItemValue.get_selected_item_renderer_class`.

    See :doc:`viewhelpers_listbuilder` for more information about listbuilder.
    """

    #: The template used to render this renderable.
    template_name = "cradmin_legacy/viewhelpers/multiselect2/listbuilder_itemvalues/itemvalue.django.html"

    #: Selected item rendrerer class.
    selected_item_renderer_class = selected_item_renderer.SelectedItem

    def __init__(self, *args, **kwargs):
        """
        Args:
            target_dom_id: See :meth:`~.ItemValue.get_target_dom_id`.
            is_selected: Mark the item as selected on load.
        """
        self.target_dom_id = kwargs.pop("target_dom_id", None)
        super().__init__(*args, **kwargs)
        self.selected_item_renderer = self.make_selected_item_renderer()

    def get_target_dom_id(self):
        """
        Returns:
            str: The ``dom_id`` of the :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`.

            Defaults to the ``target_dom_id`` parameter falling back on
            :obj:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target.default_target_dom_id`.
        """
        if self.target_dom_id:
            return self.target_dom_id
        else:
            return target_renderer.Target.default_target_dom_id

    def get_selectbutton_dom_id(self):
        """
        Returns:
            str: Get the DOM id of the select button.

            Defaults to ``cradmin_legacy_multiselect2_selectbutton_<self.value.pk>``.

            If you have multiple lists with multiselect2 on the same page, you must
            make sure this is unique.
        """
        return f"cradmin_legacy_multiselect2_selectbutton_{self.value.pk}"

    def get_base_css_classes_list(self):
        """
        Adds the ``cradmin-legacy-multiselect2-itemvalue`` css class
        in addition to the classes added by the superclasses.
        """
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-multiselect2-itemvalue")
        return css_classes

    def get_selectbutton_text(self):
        """
        Returns:
            str: The text for the select button.

            Defaults to ``"Select"`` (translatable).
        """
        return pgettext_lazy("multiselect2 select button", "Select")

    def get_selectbutton_aria_label(self):
        """
        Returns:
            str: The text for the aria-label of the select button.

            Defaults to ``"Select <self.get_title()>"`` (translatable).
        """
        return pgettext_lazy("multiselect2 select button", 'Select "%(title)s"') % {"title": self.get_title()}

    def get_custom_data(self):
        """
        Returns:
            dict: Custom data for the ``custom_data``-attribute for the angularjs directive.

            Used by :meth:`.get_select_directive_dict`.
        """
        return None

    def get_select_directive_dict(self, request):
        """
        Get options for the ``cradmin-legacy-multiselect2-select`` angularjs
        directive.

        Args:
            request: A Django HttpRequest object.

        Returns:
            dict: With options for the directive.
        """
        return {
            "preview_container_css_selector": ".cradmin-legacy-multiselect2-itemvalue",
            "preview_css_selector": ".cradmin-legacy-multiselect2-selected-item",
            "item_wrapper_css_selector": "li",
            "target_dom_id": self.get_target_dom_id(),
            "custom_data": self.get_custom_data(),
            "is_selected": self.kwargs.get("is_selected", False),
        }

    def get_select_directive_json(self, request):
        """
        Args:
            request: A Django HttpRequest object.

        Returns:
            str: The return value of :meth:`.get_select_directive_dict`
            as a json encoded and xml attribute encoded string.
        """
        return quoteattr(json.dumps(self.get_select_directive_dict(request=request)))

    def get_selected_item_renderer_class(self):
        """
        Returns:
            SelectedItem class: The renderable class to use
            to render the selected item in the corresponding
            :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`.

            Must be :class:`cradmin_legacy.viewhelpers.multiselect2.selected_item_renderer.SelectedItem`
            or a subclass.

            Defaults to :obj:`.selected_item_renderer_class`.
        """
        return self.selected_item_renderer_class

    def make_selected_item_renderer(self):
        """
        Returns:
            cradmin_legacy.viewhelpers.multiselect2.selected_item_renderer.SelectedItem: An instance
            of :meth:`.get_selected_item_renderer_class`.

            This is called in ``__init__`` and the return value is stored in ``self.selected_item_renderer``.
        """
        return self.get_selected_item_renderer_class()(value=self.value)

    def get_context_data(self, request=None):
        context = super().get_context_data(request=request)
        context["select_directive_json"] = self.get_select_directive_json(request=request)
        return context


class ManyToManySelect(ItemValue):
    """
    Many-to-many select item value.

    Extends :class:`.ItemValue` with the data needed for
    :class:`cradmin_legacy.viewhelpers.multiselect2.manytomanywidget.Widget`.
    """

    def get_manytomanyfield_preview_renderer_class(self):
        """
        Returns:
            cradmin_legacy.viewhelpers.multiselect2.widget_preview_renderer.Value: The class
            used to render the preview html (see :meth:`.get_manytomanyfield_preview_html`).
        """
        return widget_preview_renderer.Value

    def get_manytomanyfield_preview_html(self):
        """
        Returns:
            str: Preview HTML added as the ``preview`` key in :meth:`.get_custom_data`.
            This is added to the preview list rendered by
            :class:`cradmin_legacy.viewhelpers.multiselect2.manytomanywidget.Widget`
            when the selection is confirmed.
        """
        renderer_class = self.get_manytomanyfield_preview_renderer_class()
        return renderer_class(value=self.value, wrap_in_li_element=True).render()

    def get_custom_data(self):
        """
        Returns:
            dict: A dict with:

            - ``value``: Taken from the ``get_inputfield_value`` method
              of :meth:`.ItemValue.make_selected_item_renderer`. See
              :meth:`~cradmin_legacy.viewhelpers.multiselect2.selected_item_renderer.SelectedItem.get_inputfield_value`.
            - ``preview``: Preview HTML returned by :meth:`.get_manytomanyfield_preview_html`.
        """
        return {
            "value": self.selected_item_renderer.get_inputfield_value(),
            "preview": self.get_manytomanyfield_preview_html(),
        }
