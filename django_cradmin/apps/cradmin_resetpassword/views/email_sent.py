from django.views.generic import TemplateView

from django_cradmin import javascriptregistry
from django_cradmin.apps.cradmin_resetpassword.views.begin import PasswordResetEmail


class EmailSentView(TemplateView, javascriptregistry.viewmixin.StandaloneBaseViewMixin):
    template_name = "cradmin_resetpassword/email_sent.django.html"

    def get_context_data(self, **kwargs):
        context = super(EmailSentView, self).get_context_data(**kwargs)
        self.add_javascriptregistry_component_ids_to_context(context=context)
        context["email_subject"] = PasswordResetEmail().render_subject()
        return context
