from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView, UsernameLoginForm


class CustomUsernameLoginForm(UsernameLoginForm):
    username_field = 'shortname'
    shortname = forms.CharField(
        label=_('Username'))

    def clean(self):
        """
        validate the form, and execute :func:`django.contrib.auth.authenticate` to login the user if form is valid.
        """
        username = self.cleaned_data.get(self.username_field)
        password = self.cleaned_data.get('password')
        if username and password:
            authenticated_user = self.authenticate(**{
                'username': username,
                'password': password
            })

            if authenticated_user is None:
                raise forms.ValidationError(self.error_message_invalid_login)
            elif not authenticated_user.is_active:
                raise forms.ValidationError(self.error_message_inactive)
            self.__authenticated_user = authenticated_user
        return self.cleaned_data


class CustomLoginView(LoginView):
    def get_form_class(self):
        user_model = get_user_model()
        if user_model.USERNAME_FIELD == 'shortname':
            return CustomUsernameLoginForm
        return super(CustomLoginView, self).get_form_class()
