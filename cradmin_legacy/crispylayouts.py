"""
Custom django-crispy-forms layouts.
"""

from django.utils.translation import gettext_lazy
from crispy_forms import layout
from crispy_forms.helper import FormHelper
from crispy_forms.utils import flatatt
from django.template.loader import render_to_string
from cradmin_legacy.templatetags.cradmin_legacy_icon_tags import cradmin_icon


class CradminSubmitButton(layout.Submit):
    template = "cradmin_legacy/crispylayouts/submitbutton.django.html"
    extra_button_attributes = {}
    button_css_classes = "btn btn-default"

    def get_extra_button_attributes(self):
        return self.extra_button_attributes

    def __init__(self, name, value, icon_cssclass=None, **kwargs):
        self.extra_button_attributes = flatatt(self.get_extra_button_attributes())
        self.icon_cssclass = icon_cssclass
        super().__init__(name, value, **kwargs)
        self.field_classes = self.button_css_classes


class PrimarySubmit(CradminSubmitButton):
    button_css_classes = "btn btn-primary"


class PrimarySubmitBlock(CradminSubmitButton):
    button_css_classes = "btn btn-primary btn-block"


class PrimarySubmitLg(CradminSubmitButton):
    button_css_classes = "btn btn-primary btn-lg"


class DangerSubmit(CradminSubmitButton):
    button_css_classes = "btn btn-danger"


class DangerSubmitBlock(CradminSubmitButton):
    button_css_classes = "btn btn-danger btn-block"


class DefaultSubmit(CradminSubmitButton):
    button_css_classes = "btn btn-default"


class DefaultSubmitBlock(CradminSubmitButton):
    button_css_classes = "btn btn-default btn-block"


class CollapsedSectionLayout(layout.Div):
    wrapper_template_name = "cradmin_legacy/crispylayouts/collapsed-section-layout.django.html"

    def __init__(self, *args, **kwargs):
        self.show_label = kwargs.pop("show_label", gettext_lazy("Show"))
        self.hide_label = kwargs.pop("hide_label", gettext_lazy("Hide"))
        self.show_icon = kwargs.pop("show_icon", cradmin_icon("caret-down"))
        self.hide_icon = kwargs.pop("hide_icon", cradmin_icon("caret-up"))
        super().__init__(*args, **kwargs)

    def get_wrapper_context_data(self):
        return {
            "show_label": self.show_label,
            "hide_label": self.hide_label,
            "show_icon": self.show_icon,
            "hide_icon": self.hide_icon,
        }

    def render(self, *args, **kwargs):
        content = super().render(*args, **kwargs)
        context = {"content": content}
        context.update(self.get_wrapper_context_data())
        return render_to_string(self.wrapper_template_name, context)


class CradminFormHelper(FormHelper):
    template = "cradmin_legacy/crispylayouts/cradmin_form_helper.django.html"
