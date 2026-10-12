from django.utils.translation import pgettext_lazy, pgettext

from . import form_mixins
from . import container


class AbstractLabel(container.AbstractContainerRenderable):
    template_name = "django_cradmin/uicontainer/label/label.django.html"

    def get_default_html_tag(self):
        return "label"

    @property
    def for_attribute(self):
        return False

    def get_html_element_attributes(self):
        html_element_attributes = super(AbstractLabel, self).get_html_element_attributes()
        html_element_attributes["for"] = self.for_attribute
        return html_element_attributes

    @property
    def label_text(self):
        """
        The label text.

        Must be overridden in subclasses.
        """
        raise NotImplementedError()

    @property
    def label_text_aria_suffix(self):
        """
        If this returns a non-empty value, we render this after the label
        text in a ``<span>`` with class ``screenreader-only``.
        """
        return None

    @property
    def field_renderable(self):
        raise NotImplementedError()

    def should_show_text_after_field(self):
        return False


class Label(AbstractLabel, form_mixins.FieldWrapperRenderableChildMixin):
    """
    Renders a label for a :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`.

    You never use this on its own outside a
    :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`.
    """

    def __init__(self, text=None, include_optional_text=True, **kwargs):
        self._overridden_label_text = text
        self._include_optional_text = include_optional_text
        super(Label, self).__init__(**kwargs)

    def should_include_for_attribute(self):
        return (
            self.field_wrapper_renderable.field_renderable.should_have_for_attribute_on_label()
            and not self.field_wrapper_renderable.field_renderable.should_render_as_child_of_label()
        )

    def get_default_dom_id(self):
        return "{field_dom_id}_label".format(field_dom_id=self.field_wrapper_renderable.field_renderable.dom_id)

    def field_is_checkbox_input_widget(self):
        field_renderable = self.field_wrapper_renderable.field_renderable
        if hasattr(field_renderable, "is_checkbox_input_widget"):
            return field_renderable.is_checkbox_input_widget()
        else:
            return False

    def get_default_bem_block_or_element(self):
        """
        Default BEM block is ``label``.
        """
        if self.field_is_checkbox_input_widget():
            return "checkbox"
        else:
            return "label"

    @property
    def for_attribute(self):
        if self.should_include_for_attribute():
            return self.field_wrapper_renderable.field_renderable.label_for_dom_id
        else:
            return False

    @property
    def label_text(self):
        if self._overridden_label_text:
            return self._overridden_label_text
        bound_formfield = self.field_wrapper_renderable.bound_formfield
        if bound_formfield.field.label:
            return bound_formfield.field.label
        else:
            return bound_formfield.name

    @property
    def field_renderable(self):
        if self.field_wrapper_renderable.field_renderable.should_render_as_child_of_label():
            return self.field_wrapper_renderable.field_renderable
        else:
            return None

    @property
    def required(self):
        return self.field_wrapper_renderable.bound_formfield.field.required

    @property
    def include_optional_text(self):
        if self.field_is_checkbox_input_widget():
            return False
        else:
            return self._include_optional_text

    @property
    def optional_text(self):
        return pgettext_lazy("django_cradmin optional form field label suffix", "optional")

    def should_show_text_after_field(self):
        return self.field_is_checkbox_input_widget()


class SubWidgetLabel(AbstractLabel, form_mixins.FieldChildMixin):
    """
    Basic label for a Django SubWidget.

    Assumes that we want ot render the Django SubWidget within the label.

    If you want
    """

    def __init__(self, subwidget_field_renderable, **kwargs):
        self.subwidget_field_renderable = subwidget_field_renderable
        super(SubWidgetLabel, self).__init__(**kwargs)

    def prepopulate_virtual_children_list(self):
        return [self.subwidget_field_renderable]

    def should_show_text_after_field(self):
        return True

    def get_default_dom_id(self):
        return "{field_dom_id}_{index_in_parent}_label".format(
            field_dom_id=self.field_renderable.dom_id, index_in_parent=self.subwidget_field_renderable.index_in_parent
        )

    @property
    def label_text(self):
        return self.subwidget_field_renderable.label_text

    @property
    def label_text_aria_suffix(self):
        label_renderable = self.field_wrapper_renderable.label_renderable
        field_label = getattr(label_renderable, "label_text", None)
        if field_label:
            return "- {prefix} {field_label}".format(
                prefix=pgettext("uicontainer label aria text prefix", "Choice for"), field_label=field_label
            )
        else:
            return None

    @property
    def field_renderable(self):
        return self.subwidget_field_renderable


class StyledSubWidgetLabel(SubWidgetLabel):
    """
    A ``<label>`` for checkbox or radio list where we
    assumes that you want to hide the actual input field
    and style it with a _control indicator_ span.

    The control indicator span element css class will
    be ``<BEM block>__control-indicator`` - can be overriden
    in :meth:`~.StyledSubWidgetLabel.control_indicator_bem_element`.
    """

    template_name = "django_cradmin/uicontainer/label/styled_sub_widget_label.django.html"

    @property
    def control_indicator_bem_element(self):
        return "{}__control-indicator".format(self.get_bem_block_or_element())


class RadioSubWidgetLabel(StyledSubWidgetLabel):
    """
    A ``<label>`` suitable for wrapping around lists of
    radio buttons.
    """

    def get_default_bem_block_or_element(self):
        """
        Uses the ``radio`` BEM block by default.
        """
        return "radio"

    def get_default_bem_variant_list(self):
        """
        Uses the ``radio--block`` BEM variant by default.
        """
        return ["block"]


class CheckboxSubWidgetLabel(StyledSubWidgetLabel):
    """
    A ``<label>`` suitable for wrapping around lists of
    checkboxes.
    """

    def get_default_bem_block_or_element(self):
        """
        Uses the ``checkbox`` BEM block by default.
        """
        return "checkbox"

    def get_default_bem_variant_list(self):
        """
        Uses the ``checkbox--block`` BEM variant by default.
        """
        return ["block"]
