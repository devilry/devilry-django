from django.conf import settings
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView, UsernameLoginForm


class DevilryUsernameLoginForm(UsernameLoginForm):
    def model_sanity_check(self):
        # Overridden because the superclass requires
        # self.username_field == user_model.USERNAME_FIELD
        pass


class CustomLoginView(LoginView):
    def get_form_class(self):
        if not getattr(settings, 'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND', False):
            return DevilryUsernameLoginForm
        return super(CustomLoginView, self).get_form_class()
