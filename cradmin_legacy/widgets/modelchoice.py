import urllib.parse

from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy


class ModelChoiceWidget(widgets.TextInput):
    """
    Model choice widget that uses an iframe popup to enable users
    to select their foreign key value.
    """

    #: The template used to render the widget.
    template_name = "cradmin_legacy/widgets/modelchoice.django.html"

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
    default_selectbutton_text = gettext_lazy("Select ...")

    def __init__(self, queryset, selectview_url, preview="", selectbutton_text=None):
        self.queryset = queryset
        self.preview = preview
        self.selectview_url = selectview_url
        self.selectbutton_text = selectbutton_text or self.default_selectbutton_text
        super().__init__()

    def __make_selectview_url(self, fieldid, current_value):
        return "{}?{}".format(
            self.selectview_url,
            urllib.parse.urlencode(
                {
                    "foreignkey_select_current_value": current_value,
                    "foreignkey_select_fieldid": fieldid,
                }
            ),
        )

    def get_rendered_input_type(self):
        if self.input_field_visible:
            return "text"
        else:
            return "hidden"

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""
        fieldid = attrs["id"]
        return render_to_string(
            self.template_name,
            {
                "preview": self.preview,
                "fieldname": name,
                "fieldid": fieldid,
                "fieldvalue": value,
                "selectview_url": self.__make_selectview_url(fieldid, value),
                "selectbutton_text": self.selectbutton_text,
                "input_type": self.input_type,
                "rendered_input_type": self.get_rendered_input_type(),
            },
        )
