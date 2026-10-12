from django_cradmin.uicontainer import messagescontainer

from . import container
from . import form_mixins
from . import field
from . import label
from . import field_help_text


class FieldWrapper(container.AbstractContainerRenderable, form_mixins.FormRenderableChildMixin):
    """
    Renders a form field.

    This just renders a wrapper ``div``, and lets other renderable classes
    render the field, label, etc.:

    - A :class:`~django_cradmin.uicontainer.label.Label` renders the label.
      This can be overridden using the ``label_renderable`` kwarg, or in
      :meth:`.get_default_label_renderable`.
    - A :class:`~django_cradmin.uicontainer.field.BaseFieldRenderable` renders the
      form field. This can be overridden using the ``field_renderable`` kwarg,
      or in :meth:`.get_default_field_renderable`.
    - A :class:`~django_cradmin.uicontainer.help_text.AutomaticHelpText`
      renders the help text. This can be overridden using the ``help_text_renderable``
      kwarg, or in :meth:`.get_default_help_text_renderable`.
    """

    template_name = "django_cradmin/uicontainer/fieldwrapper.django.html"

    def __init__(
        self,
        fieldname,
        label_renderable=None,
        field_renderable=None,
        help_text_renderable=None,
        messages_container=None,
        **kwargs,
    ):
        self.fieldname = fieldname
        self.label_renderable = label_renderable or self.get_default_label_renderable()
        self.field_renderable = field_renderable or self.get_default_field_renderable()
        self.help_text_renderable = help_text_renderable or self.get_default_help_text_renderable()
        self.messages_container = messages_container or self.get_default_messages_container()
        super(FieldWrapper, self).__init__(**kwargs)
        self.properties["field_wrapper_renderable"] = self

    def get_default_dom_id(self):
        return "{}_wrapper".format(self.field_renderable.dom_id)

    def bootstrap(self, **kwargs):
        """
        Extends :meth:`django_cradmin.uicontainer.container.container.AbstractContainerRenderable.bootstrap`
        with a call to
        :meth:`django_cradmin.uicontainer.form.Form.register_field_wrapper_renderable`
        to register this with the form.
        """
        returnvalue = super(FieldWrapper, self).bootstrap(**kwargs)
        self.formrenderable.register_field_wrapper_renderable(field_wrapper_renderable=self)
        return returnvalue

    def get_default_html_tag(self):
        return "div"

    def get_default_label_renderable(self):
        """
        Get the default label renderable.

        This is used unless it is overridden using the ``label_renderable``
        kwarg for :meth:`.__init__`.

        Defaults to an object of :class:`~django_cradmin.uicontainer.label.Label`.
        """
        return label.Label()

    def get_default_field_renderable(self):
        """
        Get the default field renderable.

        This is used unless it is overridden using the ``field_renderable``
        kwarg for :meth:`.__init__`.

        Defaults to an object of
        :class:`~django_cradmin.uicontainer.field.Field`.
        """
        return field.Field()

    def get_default_help_text_renderable(self):
        """
        Get the default help text renderable.

        This is used unless it is overridden using the ``help_text_renderable``
        kwarg for :meth:`.__init__`.

        Defaults to an object of :class:`~django_cradmin.uicontainer.help_text.AutomaticHelpText`.
        """
        return field_help_text.AutomaticHelpText()

    def get_default_messages_container(self):
        """
        Get the default message container.

        This is used unless it is overridden using the ``messages_container``
        kwarg for :meth:`.__init__`.

        Defaults to a :class:`django_cradmin.uicontainer.messagecontainer.MessagesContainer`.

        Must implement :class:`django_cradmin.uicontainer.messagecontainer.AbstractMessageListMixin`.
        """
        return messagescontainer.CompactMessagesContainer(test_css_class_suffixes_list=["field-messages"])

    def prepopulate_virtual_children_list(self):
        """
        Pre-populates the virtual children list with:

        - Label renderable
        - Field renderable
        """
        return [self.label_renderable, self.field_renderable]

    def prepopulate_children_list(self):
        """
        Pre-populates the children list with:

        - Help text renderable.
        - Message renderable.

        See :meth:`django_cradmin.uicontainer.container.container.AbstractContainerRenderable.prepopulate_children_list`
        for details about what this method works, and what it should return.
        """
        return [
            self.help_text_renderable,
            self.messages_container,
        ]

    @property
    def bound_formfield(self):
        """
        Get the :class:`django.forms.boundfield.BoundField` for the form field.
        """
        return self.formrenderable.form[self.fieldname]

    def get_default_bem_block_or_element(self):
        return "fieldwrapper"


class NoWrapperElementFieldWrapper(FieldWrapper):
    """
    Same as :class:`.FieldWrapper` except that it does not include the wrapper
    element.
    """

    template_name = "django_cradmin/uicontainer/fieldwrapper_no_wrapper_element.django.html"
