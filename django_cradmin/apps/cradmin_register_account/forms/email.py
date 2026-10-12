from django_cradmin import uicontainer
from django_cradmin.apps.cradmin_register_account.forms.base import AbstractCreateAccountWithPasswordForm


class EmailUserCreateAccountForm(AbstractCreateAccountWithPasswordForm):
    r"""
    A create account form for a custom user model with an
    email field and a ``set_password()``-method.

    Can be used directly as the ``DJANGO_CRADMIN_REGISTER_ACCOUNT_FORM_CLASS``
    setting, or extended to create a custom register account form.

    To use it directly, set the following setting::

        DJANGO_CRADMIN_REGISTER_ACCOUNT_FORM_CLASS = \
            'django_cradmin.apps.cradmin_register_account.forms.email.EmailUserCreateAccountForm'

    The form only includes username, email and password. To add more fields, simply
    override the Meta-class and the field layout. Lets say we want to make
    a form that includes the ``full_name`` field::

        from django_cradmin.apps.cradmin_register_account.forms.auth_user import EmailUserCreateAccountForm

        class AuthUserCreateAccountWithFullNameForm(EmailUserCreateAccountForm):
            class Meta(EmailUserCreateAccountForm.Meta):
                fields = ['username', 'full_name']

            def get_field_renderables(self):
                field_renderables = super(AuthUserCreateAccountWithFullNameForm).get_field_renderables()
                field_renderables.insert(0, uicontainer.fieldwrapper.FieldWrapper(fieldname='full_name))
                return field_renderables

    """

    class Meta(AbstractCreateAccountWithPasswordForm.Meta):
        fields = ["email"]

    def deactivate_user(self, user):
        user.is_active = False

    def get_field_renderables(self):
        return [
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname="email", field_renderable=uicontainer.field.Field(autofocus=True)
            ),
            uicontainer.fieldwrapper.FieldWrapper(fieldname="password1"),
            uicontainer.fieldwrapper.FieldWrapper(fieldname="password2"),
        ]
