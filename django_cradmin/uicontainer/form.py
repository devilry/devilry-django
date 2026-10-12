from django.utils.translation import gettext_lazy

from . import container
from . import messagescontainer


class Form(container.AbstractContainerRenderable):
    """
    Renderable for a ``<form>``.
    """

    template_name = "django_cradmin/uicontainer/form.django.html"

    def __init__(
        self, form, action=None, method=None, messages_container=None, disable_submit_on_enter=False, **kwargs
    ):
        """

        Args:
            form: The Django form to render.
            action: The action attribute of the HTML form.
                If this is ``None`` (the default), we will
                use :meth:`django.http.HttpRequest.get_full_path`.
                Use ``False`` to not include an action attribute.
            method: The method attribute of the HTML form.
                Defaults to :meth:`.get_default_method` if not specified.
            messages_container: A :class:`django_cradmin.uicontainer.container.AbstractContainerRenderable`
                object where we add and render messages such as global errors and info messages.
                Defaults to :meth:`.get_default_messages_container`.

            **kwargs: Kwargs for :class:`django_cradmin.uicontainer.container.AbstractContainerRenderable`.
        """
        self._disable_submit_on_enter = disable_submit_on_enter
        self.form = form
        self.action = action
        self._overridden_method = method
        self.messages_container = messages_container or self.get_default_messages_container()
        self._fieldrenderable_map = {}
        super(Form, self).__init__(**kwargs)
        self.properties["formrenderable"] = self

    def get_default_dom_id(self):
        return "id_form"

    def prepopulate_children_list(self):
        if self.messages_container:
            return [self.messages_container]
        else:
            return []

    def get_default_html_tag(self):
        return "form"

    def get_default_method(self):
        """
        Get the default value for the method attribute of the form element.

        Defaults to ``"POST"``.
        """
        return "POST"

    @property
    def method(self):
        """
        Get the value for the method attribute of the form element.

        You should not override this. Override :meth:`.get_default_method` instead.
        """
        return self._overridden_method or self.get_default_method()

    def action_is_redirect_to_self(self):
        return self.action is None

    def disable_submit_on_enter(self):
        return self._disable_submit_on_enter

    def get_html_element_attributes(self):
        html_element_attributes = super(Form, self).get_html_element_attributes()
        html_element_attributes["method"] = self.method
        if not self.action_is_redirect_to_self():
            # if action is ``None`` (I.E.: redirect to self), we add this attribute in the
            # template, so it is not added here.
            # We have to do it this way because we do not have access to the request
            # object here.
            html_element_attributes["action"] = self.action
        return html_element_attributes

    def register_field_wrapper_renderable(self, field_wrapper_renderable):
        """
        Register a :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`
        with this form.

        The form can access all its fields via :meth:`.get_field_wrapper_renderable`
        and :meth:`.iter_field_wrapper_renderables`.

        Args:
            field_wrapper_renderable: A :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`
                object.
        """
        self._fieldrenderable_map[field_wrapper_renderable.fieldname] = field_wrapper_renderable

    def get_field_wrapper_renderable(self, fieldname):
        """
        Get a :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`
        that is a child of the form.

        Args:
            fieldname (str): A fieldname for a FieldWrapper that is a child
                of the form. Does not need to be a direct child.

        Raises:
            KeyError: If no FieldWrapper with the provided ``fieldname`` exists
                within the form.

        Returns:
            The FieldWrapper with the provided ``fieldname``.
        """
        return self._fieldrenderable_map[fieldname]

    def iter_field_wrapper_renderables(self):
        """
        Get an iterator over all the
        :class:`~django_cradmin.uicontainer.fieldwrapper.FieldWrapper`
        objects within the form.
        """
        return self._fieldrenderable_map.values()

    def get_default_messages_container(self):
        """
        Get the default message container. Used unless
        the ``messages_container`` kwarg for :meth:`.__init__` overrides it.

        Defaults to a :class:`django_cradmin.uicontainer.messagecontainer.MessagesContainer`.

        Must implement :class:`django_cradmin.uicontainer.messagecontainer.AbstractMessageContainerMixin`.
        """
        return messagescontainer.BoxMessagesContainer(test_css_class_suffixes_list=["form-globalmessages"])

    def validate(self):
        if self.form.is_valid():
            self.form_valid()
        else:
            self.form_invalid()

    def form_valid(self):
        pass

    def add_global_form_validation_errors(self, validationerror_list):
        self.messages_container.add_validationerror_list(validationerror_list=validationerror_list)

    def add_global_field_errors_message(self):
        self.messages_container.add_warning(text=gettext_lazy("Please fix the errors below."))

    def add_field_validation_errors(self, field_wrapper_renderable, validationerror_list):
        field_wrapper_renderable.messages_container.add_validationerror_list(validationerror_list=validationerror_list)

    def add_field_validation_errors_field_not_child(self, fieldname, validationerror_list):
        field_label = self.form.fields[fieldname].label
        if not field_label:
            field_label = fieldname
        self.messages_container.add_validationerror_list(validationerror_list=validationerror_list, prefix=field_label)

    def form_invalid(self):
        has_field_errors = False
        for fieldname, validationerror_list in self.form.errors.as_data().items():
            if fieldname == "__all__":
                self.add_global_form_validation_errors(validationerror_list=validationerror_list)
            else:
                try:
                    field_wrapper_renderable = self.get_field_wrapper_renderable(fieldname=fieldname)
                except KeyError:
                    self.add_field_validation_errors_field_not_child(
                        fieldname=fieldname, validationerror_list=validationerror_list
                    )
                else:
                    has_field_errors = True
                    self.add_field_validation_errors(
                        field_wrapper_renderable=field_wrapper_renderable, validationerror_list=validationerror_list
                    )

        if has_field_errors:
            self.add_global_field_errors_message()

    def bootstrap(self, **kwargs):
        result = super(Form, self).bootstrap(**kwargs)
        self.validate()
        return result
