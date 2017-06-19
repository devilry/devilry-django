from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView, UsernameLoginForm


class CustomUsernameLoginForm(UsernameLoginForm):
    username_field = 'shortname'
    shortname = forms.CharField(
        label=_('Username'))

    def authenticate(self, **kwargs):
        username = kwargs.get(self.username_field)
        password = kwargs.get('password')
        return super(CustomUsernameLoginForm, self).authenticate(username=username, password=password)


class CustomLoginView(LoginView):
    def get_form_class(self):
        if not getattr(settings, 'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND', False):
            return CustomUsernameLoginForm
        return super(CustomLoginView, self).get_form_class()
