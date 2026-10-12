from django.views.generic import TemplateView

from cradmin_legacy.apps.cradmin_resetpassword.views.begin import PasswordResetEmail


class EmailSentView(TemplateView):
    template_name = "cradmin_resetpassword/email_sent.django.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email_subject"] = PasswordResetEmail().render_subject()
        return context
