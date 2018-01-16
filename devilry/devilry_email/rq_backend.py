from django.core.mail.backends.base import BaseEmailBackend


class RQEmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):
        from . import rq_jobs
        for message in email_messages:
            rq_jobs.async_send_email_message.delay(email_message=message, fail_silently=self.fail_silently)
        return len(email_messages)
