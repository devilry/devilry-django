from smtplib import SMTPException
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_message(subject, message, *user_objects_to_send_to):
    if not settings.DEVILRY_SEND_EMAIL_TO_USERS:
        return

    message += "\n\n--\n"
    message += settings.DEVILRY_EMAIL_SIGNATURE
    emails = []

    for u in user_objects_to_send_to:
        if u.email == None or u.email.strip() == '':
            errmsg = "User {0} has no email address.".format(u.username)
            logger.error(errmsg)
        else:
            emails.append(u.email)
    subject = settings.EMAIL_SUBJECT_PREFIX + subject
    try:
        send_mail(subject, message, settings.DEVILRY_EMAIL_DEFAULT_FROM,
                  emails, fail_silently=False)
    except SMTPException, e:
        errormsg = ('SMTPException when sending email to users {users} on addresses {emails}. '
                    'Exception: {exception}'.format(users = ','.join([u.username for u in user_objects_to_send_to]),
                                                    exception = e))
        logger.error(errormsg)
    else:
        if settings.DEBUG:
            logger.debug('Email sent to: {emails}\nSubject: {subject}\n'
                         'Body:\n{message}'.format(emails = ','.join(emails),
                                                   subject = subject,
                                                   message = message))


def send_templated_message(subject, template_name, template_dictionary, *user_objects_to_send_to):
    message = render_to_string(template_name, template_dictionary)
    send_message(subject, message, *user_objects_to_send_to)
