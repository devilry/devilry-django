from django.conf import settings
from django.core import mail
from django_rq import job


@job(settings.DEVILRY_RQ_EMAIL_BACKEND_QUEUENAME)
def async_send_email_message(email_message, fail_silently):
    connection = mail.get_connection(backend=settings.DEVILRY_LOWLEVEL_EMAIL_BACKEND, fail_silently=fail_silently)
    connection.send_messages([email_message])
