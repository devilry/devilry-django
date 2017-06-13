from django.contrib.auth import get_user_model
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView, UsernameLoginForm


class CustomLoginView(LoginView):
    def get_form_class(self):
        user_model = get_user_model()
        if user_model.USERNAME_FIELD == 'shortname':
            return UsernameLoginForm
        return super(CustomLoginView, self).get_form_class()