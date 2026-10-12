import json
import urllib.parse

from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDict
from django.utils.translation import pgettext_lazy

from cradmin_legacy.viewhelpers.multiselect2 import widget_preview_renderer


class Widget(widgets.TextInput):
    """
    Model multi choice widget that uses an iframe popup to enable users
    to select values for many-to-many and one-to-many fields.
    """

    #: The template used to render the widget.
    template_name = "cradmin_legacy/viewhelpers/multiselect2/manytomanywidget/widget.django.html"

    #: Do not override this (if you set this to hidden, the widget is not rendered correctly).
    input_type = "text"

    #: Set this to ``True`` to debug the value of the input field.
    #: Setting this to ``True``, makes the ``type`` of the actually
    #: submitted input field to ``text`` instead of ``hidden``.
    #: Probably only useful for debugging.
    input_field_visible = False

    #: The default select-button text. You can override this in a subclass,
    #: or use the ``selectbutton_text``-argument for the constructor to
    #: change the button text.
    default_selectbutton_text = pgettext_lazy("multiselect2 manytomanywidget", "Select ...")

    def __init__(self, queryset, selectview_url, selectbutton_text=None, required=True):
        """
        Args:
            queryset: A :class:`django.db.models.QuerySet`.
            selectview_url: The URL of the view used to select items.
            selectbutton_text: Select button text.
                Defaults to :obj:`~.Widget.selectbutton_text`.
            required: If this is ``False``, empty selection is allowed.
        """
        self.queryset = queryset
        self.selectview_url = selectview_url
        self.selectbutton_text = selectbutton_text or self.default_selectbutton_text
        self.required = required
        super().__init__()

    def __make_selectview_url(self, fieldid, fieldvalue):
        return "{}?{}".format(
            self.selectview_url,
            urllib.parse.urlencode(
                {
                    "manytomany_select_current_value": fieldvalue,
                    "manytomany_select_fieldid": fieldid,
                    "manytomany_select_required": str(self.required),
                }
            ),
        )

    def get_rendered_input_type(self):
        if self.input_field_visible:
            return "text"
        else:
            return "hidden"

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if isinstance(value, str):
            # This handles the data we get from this widget,
            # the other stuff below is just if we get data
            # from tests and other sources where it is not JSON encoded.
            return json.loads(value)
        elif isinstance(data, MultiValueDict):
            return data.getlist(name)
        else:
            return data.get(name, None)

    def get_selected_values_queryset(self, values):
        """
        Get a queryset with the objects matching the selected values.


        Args:
            values (list): The list of selected values.
                This is the ``value``-attribute sent to :meth:`.render`,
                cooerced into a list even if the value is ``None``
                or empty string (in which case it will be an empty list).

        Returns:
            A queryset containing the selected values. Defaults
            to ``self.queryset.filter(pk__in=values)``.
        """
        return self.queryset.filter(pk__in=values)

    def get_preview_renderer_list_class(self):
        """
        Returns:
            cradmin_legacy.viewhelpers.multiselect2.widget_preview_renderer.List: The listbuilder
            list class used to render the previews.
        """
        return widget_preview_renderer.List

    def get_preview_list(self, values):
        """
        Uses :class:`.get_preview_renderer_list_class` with :meth:`.get_selected_values_queryset`
        as ``value_iterable`` to create an object of the preview listbuilder list.

        Args:
            values: See :meth:`.get_selected_values_queryset`.

        Returns:
            cradmin_legacy.viewhelpers.multiselect2.widget_preview_renderer.List: An object
            of the :meth:`.get_preview_renderer_list_class` class.
        """
        return self.get_preview_renderer_list_class().from_value_iterable(
            value_iterable=self.get_selected_values_queryset(values=values)
        )

    def render(self, name, value, attrs=None):
        """
        Render the widget using :obj:`.template_name`.

        Args:
            name: The field name.
            value: The field value. Assumed to be a list, ``None`` or empty string.
                It can be a list of any kind of value, but :meth:`.get_selected_values_queryset`
                assumes it to be a list of primary keys, so you need to override that
                method if you send some other value to filter on.
            attrs: Attributes for the input field. Must contain the
                id of the field in the ``id`` key.

        Returns:
            str: The rendered widget HTML.
        """
        if value is None or value == "":
            values = []
        else:
            values = value
        fieldvalue = json.dumps(values)
        fieldid = attrs["id"]
        return render_to_string(
            self.template_name,
            {
                "preview_list": self.get_preview_list(values=values),
                "fieldname": name,
                "fieldid": fieldid,
                "fieldvalue": fieldvalue,
                "selectview_url": self.__make_selectview_url(fieldid, fieldvalue),
                "selectbutton_text": self.selectbutton_text,
                "input_type": self.input_type,
                "rendered_input_type": self.get_rendered_input_type(),
            },
        )
