from django.core.mail.backends.base import BaseEmailBackend

from devilry.devilry_developemail.models import DevelopEmail


class DevelopEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        developemails = []
        for message in email_messages:
            developemail = DevelopEmail(raw_content=message)
            developemails.append(developemail)
        DevelopEmail.objects.bulk_create(developemails)
        return len(list(email_messages))
