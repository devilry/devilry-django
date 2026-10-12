from cradmin_legacy.apps.cradmin_register_account.forms.base import AbstractCreateAccountWithPasswordForm


class EmailUserCreateAccountForm(AbstractCreateAccountWithPasswordForm):
    r"""
    A create account form for a custom user model with an
    email field and a ``set_password()``-method.

    Can be used directly as the ``CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS``
    setting, or extended to create a custom register account form.

    To use it directly, set the following setting::

        CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS = \
            'cradmin_legacy.apps.cradmin_register_account.forms.email.EmailUserCreateAccountForm'

    The form only includes username, email and password. To add more fields, simply
    override the Meta-class and the field layout. Lets say we want to make
    a form that includes the ``full_name`` field::

        from cradmin_legacy.apps.cradmin_register_account.forms.auth_user import EmailUserCreateAccountForm

        class AuthUserCreateAccountWithFullNameForm(EmailUserCreateAccountForm):
            class Meta(EmailUserCreateAccountForm.Meta):
                fields = ['username', 'full_name']

            def get_field_layout(self):
                return [
                    'email',
                    'full_name',
                    'password1',
                    'password2',
                ]

    """

    class Meta(AbstractCreateAccountWithPasswordForm.Meta):
        fields = ["email"]

    def deactivate_user(self, user):
        user.is_active = False

    def get_field_layout(self):
        return [
            "email",
            "password1",
            "password2",
        ]
