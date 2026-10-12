from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_string

from django.views.generic import FormView

from cradmin_legacy.apps.cradmin_activate_account.utils import ActivationEmail


class BeginRegisterAccountView(FormView):
    template_name = "cradmin_register_account/begin.django.html"

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        else:
            return import_string(settings.CRADMIN_LEGACY_REGISTER_ACCOUNT_FORM_CLASS)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRADMIN_LEGACY_SITENAME"] = settings.CRADMIN_LEGACY_SITENAME
        return context

    def get_success_url(self):
        return str(reverse("cradmin-register-account-email-sent"))

    def get_next_url(self):
        """
        Get the next url to go to after the account has been activated.

        Defaults to the ``CRADMIN_LEGACY_REGISTER_ACCOUNT_REDIRECT_URL``, falling back to
        the ``LOGIN_URL`` setting.
        """
        if "next" in self.request.GET:
            return self.request.GET["next"]
        else:
            return getattr(settings, "CRADMIN_LEGACY_REGISTER_ACCOUNT_REDIRECT_URL", settings.LOGIN_URL)

    def send_activation_email(self, user):
        activation_email = ActivationEmail(request=self.request, user=user, next_url=self.get_next_url())
        activation_email.send()

    def form_valid(self, form):
        user = form.save()
        self.send_activation_email(user)
        return super().form_valid(form)
