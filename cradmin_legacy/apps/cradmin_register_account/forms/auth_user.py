from django.utils.translation import gettext_lazy
from django import forms
from django.contrib.auth import get_user_model
from cradmin_legacy.apps.cradmin_register_account.forms.base import AbstractCreateAccountWithPasswordForm


class AuthUserCreateAccountForm(AbstractCreateAccountWithPasswordForm):
    r"""
    A create account form for ``auth_user``.

    Can be used directly as the ``CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS``
    setting, or extended to create a custom register account form.

    To use it directly, set the following setting::

        CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS = \
            'cradmin_legacy.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountForm'

    The form only includes username, email and password. To add more fields, simply
    override the Meta-class and the field layout. Lets say we want to make
    a form that includes the ``first_name`` and ``last_name`` fields::

        from cradmin_legacy.apps.cradmin_register_account.forms.auth_user import AuthUserCreateAccountForm

        class AuthUserCreateAccountWithFullNameForm(AuthUserCreateAccountForm):
            class Meta(AuthUserCreateAccountForm.Meta):
                fields = ['email', 'username', 'first_name', 'last_name']

            def get_field_layout(self):
                return [
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ]

    """

    class Meta(AbstractCreateAccountWithPasswordForm.Meta):
        fields = ["email", "username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        # self.fields['username'].required = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        user_model = get_user_model()
        if user_model.objects.filter(email=email).exists():
            raise forms.ValidationError(
                message=gettext_lazy("Account with this email address already exists."), code="not_unique_email"
            )
        return email

    def deactivate_user(self, user):
        user.is_active = False

    def get_field_layout(self):
        return [
            "username",
            "email",
            "password1",
            "password2",
        ]


class AuthUserCreateAccountAutoUsernameForm(AuthUserCreateAccountForm):
    r"""
    A create account form for ``auth_user`` that autocreates the username
    from the email.

    This is a subclass of :class:`.AuthUserCreateAccountForm`,
    and the examples for extending that class works for this class too.

    Can be used directly as the ``CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS``
    setting, or extended to create a custom register account form.

    To use it directly, set the following setting::

        CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS = \
            'cradmin_legacy.apps.cradmin_register_account.forms.auth_user.AuthUserCreateAccountAutoUsernameForm'

    """

    class Meta(AuthUserCreateAccountForm.Meta):
        fields = ["email"]

    def set_username(self, user):
        user.username = user.email[0:30]

    def set_extra_user_attributes(self, user):
        self.set_username(user)

    def get_field_layout(self):
        return [
            "email",
            "password1",
            "password2",
        ]
