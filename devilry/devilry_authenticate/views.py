from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView, UsernameLoginForm


class CustomUsernameLoginForm(UsernameLoginForm):
    username_field = 'shortname'
    shortname = forms.CharField(
        label=_('Username'))


class CustomLoginView(LoginView):
    def get_form_class(self):
        user_model = get_user_model()
        if user_model.USERNAME_FIELD == 'shortname':
            return CustomUsernameLoginForm
        return super(CustomLoginView, self).get_form_class()
