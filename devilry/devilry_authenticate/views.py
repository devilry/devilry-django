from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView, AbstractLoginForm

class UsernameLoginForm(AbstractLoginForm):
    """
    This form is used for username-based login.

    Using this form in its default state requires the `User`-models ``USERNAME_FIELD`` to be ``username``.
    This is set in the field ``username_field`` in this class.
    """
    username_field = 'shortname'
    username_field_placeholder = _('Username')
    username = forms.CharField(
        label=_('Username'))
    error_message_invalid_login = _("Your username and password didn't match. Please try again.")
    
    def authenticate(self, **kwargs):
        username = kwargs.get(self.username_field) 
        password = kwargs.get('password')
        return super(UsernameLoginForm, self).authenticate(username=username, password=password)

class CustomLoginView(LoginView):
    def get_form_class(self):
        if not getattr(settings, 'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND', False):
            return UsernameLoginForm
        return super(CustomLoginView, self).get_form_class()
