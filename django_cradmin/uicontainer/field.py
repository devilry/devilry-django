import datetime
import json
from xml.sax.saxutils import quoteattr

from django import forms

from django.utils.safestring import mark_safe
from django.utils.translation import gettext, pgettext

from django_cradmin.widgets import rangeinput
from . import container
from . import form_mixins
from . import label
from . import utils

if utils.has_template_based_form_rendering():
    from django.forms.renderers import get_default_renderer


class BaseFieldRenderable(container.AbstractContainerRenderable, form_mixins.FieldWrapperRenderableChildMixin):
    """
    Abstract base class for renders of the actual form field
    for a :class:`.FieldWrapper`.

    You never use this on its own outside a :class:`.FieldWrapper`.
    """

    def __init__(self, autofocus=False, placeholder=False, **kwargs):
        """

        Args:
            autofocus (boolean): Autofocus on this field at page load?
            placeholder (str): Placeholder text. See
                :meth:`~django_cradmin.uicontainer.container.AbstractContainerRenderable.get_html_element_attributes`
                for details about how values are applied.
            **kwargs: Kwargs for :class:`django_cradmin.uicontainer.container.AbstractContainerRenderable`.
        """
        self._overridden_autofocus = autofocus
        self._overridden_placeholder = placeholder
        super(BaseFieldRenderable, self).__init__(**kwargs)

    def get_default_autofocus(self):
        """
        Get the default value for the autofocus attribute of the html element.

        Defaults to ``False``.
        """
        return False

    @property
    def fieldname(self):
        return self.field_wrapper_renderable.fieldname

    @property
    def value(self):
        return self.bound_formfield.value()

    @property
    def label_for_dom_id(self):
        return self.dom_id

    @property
    def autofocus(self):
        """
        Get the value for the autofocus attribute of the html element.

        You should not override this. Override :meth:`.get_default_autofocus` instead.
        """
        return self._overridden_autofocus or self.get_default_autofocus()

    def get_default_placeholder(self):
        """
        Get the default value for the placeholder attribute of the html element.

        Defaults to ``False``.
        """
        return False

    @property
    def placeholder(self):
        """
        Get the value for the placeholder attribute of the html element.

        You should not override this. Override :meth:`.get_default_placeholder` instead.
        """
        return self._overridden_placeholder or self.get_default_placeholder()

    def get_field_element_attributes(self):
        """
        Get the attributes of the field element.

        Useful if you create a subclass where the template wraps the field
        in another element. You can then use :meth:`.get_html_element_attributes`
        to get the attributes of the wrapper element, and override this
        to set attributes on the field. See :class:`.Select` for an example.

        Defaults to :meth:`.get_html_element_attributes` with placeholder
        and autofocus added.
        """
        field_element_attributes = dict(self.get_html_element_attributes())
        field_element_attributes.update(
            {
                "autofocus": self.autofocus,
                "placeholder": self.placeholder,
            }
        )
        return field_element_attributes

    def should_have_for_attribute_on_label(self):
        """
        Should this field get a ``for`` attribute on its label?

        Used by :class:`django_cradmin.uicontainer.label.Label`.

        Defaults to ``True``, but subclasses can override this.
        """
        return True

    def should_render_as_child_of_label(self):
        """
        Should this field be renderered as a child of the ``<label>``?

        Returns ``True`` by default, but subclasses should override this
        for fields that should not be rendered within a label.

        For example, :class:`.Field` overrides this with varying behavior
        depending on the type of the Django field widget.
        """
        return True

    @property
    def bound_formfield(self):
        return self.field_wrapper_renderable.formrenderable.form[self.field_wrapper_renderable.fieldname]

    def get_default_dom_id(self):
        return self.bound_formfield.auto_id

    @property
    def field_attributes_dict(self):
        attributes_dict = {}
        attributes_dict = self.bound_formfield.build_widget_attrs(attributes_dict)
        attributes_dict.update(self.get_field_element_attributes())
        return attributes_dict


class SubWidgetField(BaseFieldRenderable):
    template_name = "django_cradmin/uicontainer/field/subwidget.django.html"

    def __init__(self, django_subwidget, index_in_parent, **kwargs):
        self.django_subwidget = django_subwidget
        self.index_in_parent = index_in_parent
        super(SubWidgetField, self).__init__(**kwargs)

    @property
    def label_text(self):
        if utils.has_template_based_form_rendering():
            return self.django_subwidget.get("label", "")
        else:
            return self.django_subwidget.choice_label

    def can_have_children(self):
        return False

    @property
    def field_attributes_dict(self):
        attributes_dict = {}
        if utils.has_template_based_form_rendering():
            attrs = self.django_subwidget.get("attrs", {})
        else:
            attrs = self.django_subwidget.attrs
        attributes_dict.update(attrs)
        attributes_dict.update(self.get_html_element_attributes())
        if self.dom_id:
            if utils.has_template_based_form_rendering():
                attributes_dict["id"] = self.dom_id
            else:
                attributes_dict["id"] = "{dom_id}_{index_in_parent}".format(
                    dom_id=self.dom_id, index_in_parent=self.index_in_parent
                )
        return attributes_dict

    @property
    def rendered_subwidget(self):
        if utils.has_template_based_form_rendering():
            renderer = get_default_renderer()
            widget = self.bound_formfield.field.widget
            attrs = self.field_attributes_dict
            attrs["id"] = self.dom_id

            option = widget.create_option(
                name=self.django_subwidget["name"],
                value=self.django_subwidget.get("value", None),
                label=self.django_subwidget.get("label"),
                selected=self.django_subwidget["selected"],
                index=self.index_in_parent,
                subindex=None,
                attrs=self.field_attributes_dict,
            )
            if isinstance(option, dict) and option.get("type") in ("checkbox", "radio"):
                option["wrap_label"] = False
            return mark_safe(
                renderer.render(template_name=self.django_subwidget["template_name"], context={"widget": option})
            )
        else:
            return self.django_subwidget.tag(attrs=self.field_attributes_dict)


class Field(BaseFieldRenderable):
    """
    Automatically renders a form field for a :class:`.FieldWrapper`
    using the Django widget system.

    You never use this on its own outside a :class:`.FieldWrapper`.

    Examples:

        First of all, this is always used within a
        :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`,
        and by default FieldWrapper uses this class without any kwargs
        as the ``field_renderable``. So the following will render a
        field on the form named ``email`` no matter what the type or
        widget of the field is::

            from django_cradmin import uicontainer

            class ExampleForm(forms.Form):
                email = forms.EmailField()

            # You would put the fieldwrapper as a child somewhere below
            # a ``django_cradmin.uicontainer.form.Form``, but we
            # do not include that in these examples for brevity. See the docs for
            # ``django_cradmin.uicontainer.form.Form`` for a complete example.
            uicontainer.fieldwrapper.FieldWrapper(fieldname='email')

        Let us adjust some parameters of the field rendered by the FieldWrapper
        by providing a custom field_renderable::

            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='email',
                field_wrapper_renderable=uicontainer.field.Field(
                    autofocus=True,  # Autofocus on page load
                    placeholder="Type your email...",  # Set a placeholder text

                    # Change the css classes - the css class of the field will
                    # be ``custom-input custom-input--big``
                    bem_block='custom-input',
                    bem_variant_list=['big']

                    # Alternatively, we can set the css class
                ))

        What about some CSS classes on the input field? We can do that using
        BEM naming, by specifying css classes directly as a list,
        or by just adding some css classes. Lets look at the BEM options::

            # Change the BEM block from ``input`` (the default) to ``custom-input``.
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='email',
                field_wrapper_renderable=uicontainer.field.Field(
                    bem_block='custom-input',
                    bem_variant_list=['big']
                ))

            # .. or just add some variants ..
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='email',
                field_wrapper_renderable=uicontainer.field.Field(
                    bem_variant_list=['inline', 'small']
                ))

            # .. or both ..
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='email',
                field_wrapper_renderable=uicontainer.field.Field(
                    bem_block='custom-input',
                    bem_variant_list=['large']
                ))

            # In all cases, the resulting CSS class will be
            # <bem_block> [<bem_block>--<variant0]  [<bem_block>--<variantN>]

        Refer to :ref:`uicontainer_styling` for more details about setting
        CSS classes.

        Field just works automatically with choice fields, but that uses a
        ``<select>`` by default. Let us render a ChoiceField as a
        radio button list instead::

            class ExampleForm(forms.Form):
                user_type = forms.ChoiceField(
                    choices=[
                        ('standard', 'Standard'),
                        ('admin', 'Admin'),
                    ],
                    initial='standard',
                    widget=forms.RadioSelect()
                )

            # Nothing special is needed - we pick up that you override
            # the widget on the form field, and just render it differently.
            uicontainer.fieldwrapper.FieldWrapper(fieldname='user_type')

            # We can override options for the sub-widgets (the radio buttons)
            # Lets change the CSS class of the label around each of the radio buttons
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='user_type',
                field_renderable=uicontainer.field.Field(
                    subwidget_renderable_kwargs={
                        'bem_variant_list': ['inline']
                    }
                )
            )

        CheckboxSelectMultiple widgets work just like the RadioSelect widget.

        If you need more customization than the ``subwidget_renderable_kwargs`` option
        provides, you can customize exactly how RadioSelect and CheckboxSelectMultiple is rendered
        by extending :class:`.Field` and override:

        - :meth:`~.Field.make_subwidget_renderable_radio`
        - :meth:`~.Field.make_subwidget_renderable_checkbox`

    """

    template_name = "django_cradmin/uicontainer/field/field.django.html"

    def __init__(self, subwidget_renderable_kwargs=None, **kwargs):
        """

        Args:
            subwidget_renderable_kwargs: Kwargs for the subwidget renderable.
                See :meth:`.make_subwidget_renderable`. You can provide any
                kwargs that works with
                :class:`~django_cradmin.uicontainer.container.AbstractContainerRenderable`.
            **kwargs: Kwargs for :class:`.BaseFieldRenderable`.
        """
        self.extra_subwidget_renderable_kwargs = subwidget_renderable_kwargs or {}
        super(Field, self).__init__(**kwargs)
        self.properties["field_wrapper_renderable"] = self

    @property
    def django_widget(self):
        """
        Get the Django Widget object for the formfield.
        """
        return self.bound_formfield.field.widget

    def is_radio_select_widget(self):
        """
        Returns ``True`` if the field widget is a :class:`django.forms.widgets.RadioSelect`.
        """
        return isinstance(self.django_widget, forms.RadioSelect)

    def is_range_widget(self):
        """
        Returns ``True`` if the field widget is a :class:`django_cradmin.widgets.rangeinput.RangeInput`.
        """
        return isinstance(self.django_widget, rangeinput.RangeInput)

    def is_checkbox_widget(self):
        """
        Returns ``True`` if the field widget is a :class:`django.forms.widgets.CheckboxInput`.
        """
        return isinstance(self.django_widget, forms.CheckboxInput)

    def is_checkbox_select_multiple_widget(self):
        """
        Returns ``True`` if the field widget is a :class:`django.forms.widgets.CheckboxSelectMultiple`.
        """
        return isinstance(self.django_widget, forms.CheckboxSelectMultiple)

    def is_select_multiple_widget(self):
        """
        Returns ``True`` if the field widget is a :class:`django.forms.widgets.SelectMultiple`.
        """
        return isinstance(self.django_widget, forms.SelectMultiple)

    def is_select_widget(self):
        """
        Returns ``True`` if the field widget is a :class:`django.forms.widgets.Select`.
        """
        return isinstance(self.django_widget, forms.Select)

    def is_checkbox_input_widget(self):
        """
        Returns ``True`` if the field widget is a :class:`django.forms.widgets.CheckboxInput`.
        """
        return isinstance(self.django_widget, forms.CheckboxInput)

    def should_render_as_subwidgets(self):
        """
        Returns True if we should render using :meth:`.make_subwidget_renderable`.

        Default to returining ``True`` if :meth:`.is_radio_select_widget` or
        :meth:`.is_checkbox_select_multiple_widget` returns ``True``.
        """
        return self.is_radio_select_widget() or self.is_checkbox_select_multiple_widget()

    def should_have_for_attribute_on_label(self):
        """
        Should this field get a ``for`` attribute on its label?

        Used by :class:`django_cradmin.uicontainer.label.Label`.

        Defaults to :meth:`.should_render_as_child_of_label`.
        """
        return not self.should_render_as_child_of_label()

    def should_render_as_child_of_label(self):
        """
        Should this field be rendered as a child of the label?

        Used by :class:`django_cradmin.uicontainer.label.Label`.
        """
        if self.is_checkbox_widget() or self.should_render_as_subwidgets():
            return True
        return False

    def get_default_bem_block_or_element(self):
        """
        Default BEM block is ``input``.
        """
        if self.is_select_widget() or self.is_checkbox_input_widget():
            return None
        elif self.is_range_widget():
            return "range-input"
        else:
            return "input"

    def get_default_bem_variant_list(self):
        return ["outlined"]

    def get_default_test_css_class_suffixes_list(self):
        return super(Field, self).get_default_test_css_class_suffixes_list() + [
            "djangowidget-{}".format(self.django_widget.__class__.__name__.lower())
        ]

    def render_bound_formfield_as_widget(self):
        return self.bound_formfield.as_widget(attrs=self.field_attributes_dict)

    def get_subwidget_renderable_kwargs(self, django_subwidget, index_in_parent):
        """
        Get kwargs for the subwidget created by :meth:`.make_subwidget_renderable`.

        Defaults to the ``subwidget_renderable_kwargs`` kwargs + adding
        a :class:`.SubWidgetField` object as ``subwidget_field_renderable``.
        """
        kwargs = dict(self.extra_subwidget_renderable_kwargs)
        kwargs.update(
            {
                "subwidget_field_renderable": SubWidgetField(
                    django_subwidget=django_subwidget, index_in_parent=index_in_parent
                )
            }
        )
        return kwargs

    def make_subwidget_renderable_radio(self, django_subwidget, index_in_parent):
        """
        Make subwidget renderable to use if :meth:`.is_radio_select_widget` returns ``True``.

        Returns a :class:`django_cradmin.uicontainer.label.RadioSubWidgetLabel`
        with kwargs from :meth:`.get_subwidget_renderable_kwargs` by default.

        Used by :meth:`.make_subwidget_renderable`.

        Args:
            django_subwidget: The SubWidget object.
            index_in_parent: The index of the subwidget in the parent.
        """
        return label.RadioSubWidgetLabel(
            **self.get_subwidget_renderable_kwargs(django_subwidget=django_subwidget, index_in_parent=index_in_parent)
        )

    def make_subwidget_renderable_checkbox(self, django_subwidget, index_in_parent):
        """
        Make subwidget renderable to use if :meth:`.is_checkbox_select_multiple_widget` returns ``True``.

        Returns a :class:`django_cradmin.uicontainer.label.CheckboxSubWidgetLabel`
        with kwargs from :meth:`.get_subwidget_renderable_kwargs` by default.

        Used by :meth:`.make_subwidget_renderable`.

        Args:
            django_subwidget: The SubWidget object.
            index_in_parent: The index of the subwidget in the parent.
        """
        return label.CheckboxSubWidgetLabel(
            **self.get_subwidget_renderable_kwargs(django_subwidget=django_subwidget, index_in_parent=index_in_parent)
        )

    def make_subwidget_renderable(self, django_subwidget, index_in_parent):
        """
        Make a renderable for a Django SubWidget.

        Only used if :meth:`.should_render_as_subwidgets` returns ``True``.

        By default this returns:

        - :meth:`.make_subwidget_renderable_radio` if :meth:`.is_radio_select_widget` returns ``True``.
        - :meth:`.make_subwidget_renderable_checkbox` if :meth:`.is_checkbox_select_multiple_widget` returns ``True``.
        - Raise NotImplementedError otherwise.

        Args:
            django_subwidget: The SubWidget object.
            index_in_parent: The index of the subwidget in the parent.

        """
        if self.is_radio_select_widget():
            return self.make_subwidget_renderable_radio(
                django_subwidget=django_subwidget, index_in_parent=index_in_parent
            )
        elif self.is_checkbox_select_multiple_widget():
            return self.make_subwidget_renderable_checkbox(
                django_subwidget=django_subwidget, index_in_parent=index_in_parent
            )
        else:
            widget_class = self.django_widget.__class__
            raise NotImplementedError(
                "The {widget_class!r} widget is not supported.".format(
                    widget_class="{}.{}".format(widget_class.__module__, widget_class.__name__)
                )
            )

    def iter_subwidgets(self):
        for index, django_subwidget in enumerate(
            self.django_widget.subwidgets(
                name=self.bound_formfield.html_name,
                value=self.bound_formfield.value(),
                attrs=self.field_attributes_dict,
            )
        ):
            subwidget = self.make_subwidget_renderable(django_subwidget=django_subwidget, index_in_parent=index)
            subwidget.bootstrap(parent=self)
            yield subwidget

    @property
    def rendered_field(self):
        return self.render_bound_formfield_as_widget()


class Select(Field):
    """
    Renders ``<select>`` wrapped in a label with
    the ``select select--outlined select--block`` css
    classes.
    """

    template_name = "django_cradmin/uicontainer/field/select.django.html"

    def get_default_bem_block_or_element(self):
        return "select"

    def get_default_html_tag(self):
        return "label"

    def get_default_bem_variant_list(self):
        return ["outlined", "block"]

    def get_html_element_attributes(self):
        html_element_attributes = super(Select, self).get_html_element_attributes()
        html_element_attributes.pop("id")
        return html_element_attributes

    def get_field_element_attributes(self):
        return {"id": self.dom_id}


class HiddenField(Field):
    """
    Just like :class:`.Field`, but renders as
    a ``<input type="hidden">``.

    Typically rendered within a :class:`django_cradmin.uicontainer.fieldwrapper.NoWrapperElementFieldWrapper`.

    Examples:

        Basic example::

            uicontainer.fieldwrapper.NoWrapperElementFieldWrapper(
                fieldname='myfield',
                field_renderable=uicontainer.field.HiddenField()
            )
    """

    @property
    def rendered_field(self):
        return self.bound_formfield.as_hidden(attrs=self.field_attributes_dict)

    def get_default_bem_block_or_element(self):
        return None


class AbstractDate(Field):
    template_name = "django_cradmin/uicontainer/field/date.django.html"

    string_datetime_formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%H:%M",
        "%H:%M:%S",
    ]

    def __init__(self, debug=False, **kwargs):
        """

        Args:
            debug (boolean): If this is ``True``, we render the input field
                as a text input instead of a hidden input.
            **kwargs: Kwargs for :class:`.Field`.
        """
        self.debug = debug
        super(AbstractDate, self).__init__(**kwargs)

    def should_render_as_child_of_label(self):
        return False

    def get_month_labels(self):
        return [
            pgettext("monthname", "Jan"),
            pgettext("monthname", "Feb"),
            pgettext("monthname", "Mar"),
            pgettext("monthname", "Apr"),
            pgettext("monthname", "May"),
            pgettext("monthname", "Jun"),
            pgettext("monthname", "Jul"),
            pgettext("monthname", "Aug"),
            pgettext("monthname", "Sep"),
            pgettext("monthname", "Oct"),
            pgettext("monthname", "Nov"),
            pgettext("monthname", "Des"),
        ]

    def make_aria_label(self, subfield_label):
        label_renderable = self.field_wrapper_renderable.label_renderable
        label_text = getattr(label_renderable, "label_text", "")
        if label_text:
            return "{} - {}".format(subfield_label, label_text)
        return subfield_label

    def make_day_field_props(self):
        return {
            "labelText": gettext("Day"),
            "extraSelectAttributes": {"aria-label": self.make_aria_label(gettext("Day"))},
        }

    def make_month_field_props(self):
        return {
            "labelText": gettext("Month"),
            "monthLabels": self.get_month_labels(),
            "extraSelectAttributes": {"aria-label": self.make_aria_label(gettext("Month"))},
        }

    def make_year_field_props(self):
        return {
            "labelText": gettext("Year"),
            "extraSelectAttributes": {"aria-label": self.make_aria_label(gettext("Year"))},
        }

    def make_hour_field_props(self):
        return {"extraInputAttributes": {"aria-label": self.make_aria_label(gettext("Hour"))}}

    def make_minute_field_props(self):
        return {"extraInputAttributes": {"aria-label": self.make_aria_label(gettext("Minute"))}}

    def make_result_field_props(self):
        if self.debug:
            input_type = "text"
        else:
            input_type = "hidden"
        return {
            "inputName": self.fieldname,
            "inputType": input_type,
        }

    def make_initial_values_dict(self, value_object):
        initial_values_dict = {}
        if isinstance(value_object, (datetime.date, datetime.datetime)):
            initial_values_dict.update(
                {
                    "initialDay": value_object.day,
                    "initialMonth": value_object.month,
                    "initialYear": value_object.year,
                }
            )
        if isinstance(value_object, (datetime.time, datetime.datetime)):
            initial_values_dict.update({"initialHour": value_object.hour, "initialMinute": value_object.minute})
        return initial_values_dict

    def get_initial_values(self):
        value = self.value
        if value and isinstance(value, str):
            value = self.make_value_object_from_string(value_string=value)
        if value:
            return self.make_initial_values_dict(value_object=value)
        return None

    def make_widget_config_dict(self):
        config_dict = {
            "signalNameSpace": self.fieldname,
            "resultFieldProps": self.make_result_field_props(),
            "dayFieldProps": self.make_day_field_props(),
            "monthFieldProps": self.make_month_field_props(),
            "yearFieldProps": self.make_year_field_props(),
            "hourFieldProps": self.make_hour_field_props(),
            "minuteFieldProps": self.make_minute_field_props(),
        }
        initial_values = self.get_initial_values()
        if initial_values:
            config_dict.update(initial_values)
        return config_dict

    def _quoted_json(self, dct):
        return mark_safe(quoteattr(json.dumps(dct)))

    def make_value_object_from_string(self, value_string):
        for datetime_format in self.string_datetime_formats:
            try:
                return datetime.datetime.strptime(value_string, datetime_format)
            except ValueError:
                pass
        return None

    def get_context_data(self, **kwargs):
        context = super(AbstractDate, self).get_context_data(**kwargs)
        context["widget_config_json"] = self._quoted_json(self.make_widget_config_dict())
        return context


class Date(AbstractDate):
    """
    Date input field renderable.

    This requires the cradmin javascript, so you will typically need
    to add::

        def get_javascriptregistry_component_ids(self):
            return ['django_cradmin_javascript']

    to your views (assuming the use one of the ``django_cradmin.viewhelpers``
    views).

    Examples:

        Basic example::

            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='birth_date',
                field_renderable=uicontainer.field.Date())
    """

    def make_widget_config_dict(self):
        widget_config_dict = super(Date, self).make_widget_config_dict()
        widget_config_dict["includeDate"] = True
        widget_config_dict["includeTime"] = False
        return widget_config_dict

    @property
    def label_for_dom_id(self):
        return "{}_daysubfield".format(self.dom_id)

    def make_day_field_props(self):
        props = super(Date, self).make_day_field_props()
        props["extraSelectAttributes"]["id"] = self.label_for_dom_id
        return props


class DateTime(AbstractDate):
    """
    DateTime input field renderable.

    This requires the cradmin javascript, so you will typically need
    to add::

        def get_javascriptregistry_component_ids(self):
            return ['django_cradmin_javascript']

    to your views (assuming the use one of the ``django_cradmin.viewhelpers``
    views).

    Examples:

        Basic example::

            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='publishing_datetime',
                field_renderable=uicontainer.field.DateTime())
    """

    @property
    def label_for_dom_id(self):
        return "{}_daysubfield".format(self.dom_id)

    def make_day_field_props(self):
        props = super(DateTime, self).make_day_field_props()
        props["extraSelectAttributes"]["id"] = self.label_for_dom_id
        return props

    def make_widget_config_dict(self):
        widget_config_dict = super(DateTime, self).make_widget_config_dict()
        widget_config_dict["includeDate"] = True
        widget_config_dict["includeTime"] = True
        return widget_config_dict


class Time(AbstractDate):
    """
    Time input field renderable.

    This requires the cradmin javascript, so you will typically need
    to add::

        def get_javascriptregistry_component_ids(self):
            return ['django_cradmin_javascript']

    to your views (assuming the use one of the ``django_cradmin.viewhelpers``
    views).

    Examples:

        Basic example::

            uicontainer.fieldwrapper.FieldWrapper(
                fieldname='current_time',
                field_renderable=uicontainer.field.Time())
    """

    @property
    def label_for_dom_id(self):
        return "{}_hoursubfield".format(self.dom_id)

    def make_hour_field_props(self):
        props = super(Time, self).make_hour_field_props()
        props["extraInputAttributes"]["id"] = self.label_for_dom_id
        return props

    def make_widget_config_dict(self):
        widget_config_dict = super(Time, self).make_widget_config_dict()
        widget_config_dict["includeDate"] = False
        widget_config_dict["includeTime"] = True
        return widget_config_dict
