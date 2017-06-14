from crispy_forms import layout
from django.contrib.auth import get_user_model
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView, UsernameLoginForm


class CustomUsernameLoginForm(UsernameLoginForm):
    username_field = 'shortname'


class CustomLoginView(LoginView):
    def get_form_class(self):
        user_model = get_user_model()
        if user_model.USERNAME_FIELD == 'shortname':
            return CustomUsernameLoginForm
        return super(CustomLoginView, self).get_form_class()

    def get_field_layout(self):
        form_class = self.get_form_class()
        return [
            layout.Field(form_class.username_field,
                         placeholder=form_class.username_field_placeholder,
                         css_class='input-lg',
                         focusonme='focusonme'),
            layout.Field('password',
                         placeholder=form_class.password_field_placeholder,
                         css_class='input-lg'),
        ]
