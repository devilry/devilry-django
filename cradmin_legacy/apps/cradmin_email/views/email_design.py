from django.http import HttpResponse
from django.views.generic import View

from cradmin_legacy.apps.cradmin_email import emailutils


class DemoEmail(emailutils.AbstractEmail):
    subject_template = "cradmin_email/cradmin_email_send_testmail/subject.django.txt"
    html_message_template = "cradmin_email/cradmin_email_send_testmail/html_message.django.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["name"] = "Test Name"
        return context


class EmailDesignView(View):
    def get(self, request, format="html"):
        email = DemoEmail()
        if format == "plaintext":
            return HttpResponse(email.render_plaintext_message(), content_type="text/plain")
        else:
            return HttpResponse(email.render_html_message())
