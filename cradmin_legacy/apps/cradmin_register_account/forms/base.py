from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy
from django import forms
from cradmin_legacy.crispylayouts import PrimarySubmitLg


class AbstractCreateAccountForm(forms.ModelForm):
    """
    Base class for account creation forms.

    Subclasses **must** override:

    - :meth:`~.AbstractCreateAccountForm.set_password`.
    - :meth:`~.AbstractCreateAccountForm.deactivate_user`.
    """

    #: Used to add custom attributes like angularjs directives to the form.
    #: See :meth:`.get_form_attributes`.
    form_attributes = {}

    class Meta:
        model = get_user_model()
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.get_formhelper()

    def get_formhelper(self):
        """
        Get a :class:`crispy_forms.helper.FormHelper`.

        You normally do not need to override this directly. Instead
        you should override:

        - :meth:`.get_field_layout`.
        - :meth:`.get_hidden_fields`
        """
        helper = FormHelper()
        layoutargs = list(self.get_field_layout()) + list(self.get_button_layout()) + list(self.get_hidden_fields())
        helper.layout = layout.Layout(*layoutargs)
        helper.form_action = "#"
        form_id = self.get_form_id()
        if form_id:
            helper.form_id = form_id
        helper.attrs = self.get_form_attributes()
        return helper

    def get_submit_button_label(self):
        """
        Returns the submit button label.

        Override this to provide a custom label.
        """
        return gettext_lazy("Sign up for %(sitename)s") % {"sitename": settings.CRADMIN_LEGACY_SITENAME}

    def get_button_layout(self):
        """
        Get the button layout. This is added to the crispy form layout.
        """
        return [
            PrimarySubmitLg("submit-register", self.get_submit_button_label()),
        ]

    def get_form_attributes(self):
        """
        You can add custom attributes to the form via this method.

        This is set as the ``attrs``-attribute of the crispy FormHelper
        created in :meth:`.get_formhelper`.

        Defaults to :obj:`.form_attributes`.

        Returns:
            A dictionary to set any kind of form attributes. Underscores in
            keys are translated into hyphens.
        """
        return self.form_attributes

    def get_form_id(self):
        """
        Returns the ID to set on the DOM element for the form.

        Defaults to `"cradmin_legacy_register_account_form"`.
        """
        return "cradmin_legacy_register_account_form"

    def get_field_layout(self):
        """
        Get a list/tuple of fields. These are added to a ``crispy_forms.layout.Layout``.

        Must be overridden.

        Simple example::

            from django.views.generic import FormView
            from crispy_forms import layout

            class MyForm(AbstractCreateAccountForm):
                def get_field_layout(self):
                    return [
                        layout.Div('name', 'username')
                    ]
        """

    def get_hidden_fields(self):
        """
        Get hidden fields for the form.

        Returns:
            An iterable of :class:`crispy_forms.layout.Hidden` objects.
            Defaults to an empty list.
        """
        return []

    def set_password(self, user):
        """
        Set the password of the given ``user``.

        **Must** be overridden in subclasses.

        Should not save the user, only set the password.

        Typically this will retrieve the password from the form, or
        generate a password, and set the password using ``user.set_password``. Example::

            class MyCreateAccountForm(AbstractCreateAccountForm):
                ...
                def set_password(self, user):
                    raw_password = 'secret'  # or self.cleaned_data['password']
                    user.set_password(raw_password)

        """
        raise NotImplementedError()

    def deactivate_user(self, user):
        """
        Mark the ``user`` as inactive.

        **Must** be overridden in subclasses.

        Should not save the user, only set it as inactive.

        Example:
            Basic example that works with the default django user model::

                class MyCreateAccountForm(AbstractCreateAccountForm):
                    ...
                    def deactivate_user(self, user):
                        user.is_active = False
        """
        raise NotImplementedError()

    def set_extra_user_attributes(self, user):
        """
        Override this to set extra user attributes in addition to
        :meth:`~.AbstractCreateAccountForm.deactivate_user` and
        :meth:`~.AbstractCreateAccountForm.set_password`.
        """

    def save(self, commit=True):
        user = super().save(commit=False)
        self.set_password(user)
        self.deactivate_user(user)
        self.set_extra_user_attributes(user)
        user.full_clean()
        if commit:
            user.save()
        return user


class AbstractCreateAccountWithPasswordForm(AbstractCreateAccountForm):
    """
    Extends :class:`.AbstractCreateAccountForm` with the typical
    password + repeat password fields. Validates that the passwords
    match.

    Subclasses **must** override:

    - :meth:`~.AbstractCreateAccountForm.deactivate_user`.
    """

    #: The first password.
    password1 = forms.CharField(label=gettext_lazy("Type your password"), widget=forms.PasswordInput)

    #: The repeat password fields.
    password2 = forms.CharField(label=gettext_lazy("Type your password one more time"), widget=forms.PasswordInput)

    def set_password(self, user):
        """
        Set the password of the user using ``user.set_password(...)``.

        Does not save the user.
        """
        raw_password = self.cleaned_data["password1"]
        user.set_password(raw_password)

    def clean(self):
        """
        Validate the form.

        The default implementation validates that the passwords
        match.

        Make sure to call super if you override this::

            class MyCreateAccountForm(AbstractCreateAccountWithPasswordForm):
                ...
                def clean(self):
                    cleaned_data = super(MyCreateAccountForm, self).clean()
                    # ...
                    return cleaned_data
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    message=gettext_lazy("The passwords do not match."), code="passwords_do_not_match"
                )
        return cleaned_data
