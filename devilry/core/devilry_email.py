from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.core.mail import mail_admins
from django.conf import settings

def send_email(user_objects_to_send_to, subject, message):
    if not settings.SEND_EMAIL_TO_USERS:
        return
    
    message += "\n\n--\n"
    message += settings.EMAIL_SIGNATURE
    emails = []

    for u in user_objects_to_send_to:
        if u.email == None or u.email.strip() == '':
            send_email_admins("Invalid email", "User %s has no email address." %
                              u.username)
        else:
            emails.append(u.email)
    try:
        send_mail(settings.EMAIL_SUBJECT_PREFIX + subject, message, settings.EMAIL_DEFAULT_FROM,
                  emails, fail_silently=False)
    except smtplib.SMTPException, e:
        send_email_admins("Invalid email", "Error when sending email to user %s on address %s. Exception: %s" %
                          (u.username, u.email, e),
                          fail_silently=False)
        raise

    # If one or more emails were not sent, a warning message is shown to the student who delivers.
    if len(emails) < len(user_objects_to_send_to):
        raise Exception()

def send_email_admins(subject, message, fail_silently=False):
    if len(settings.ADMINS) == 0:
        return
    emails = []
    for name, email in settings.ADMINS:
        emails.append(email)

    send_mail(settings.EMAIL_SUBJECT_PREFIX_ADMIN + subject, message, settings.EMAIL_DEFAULT_FROM,
              emails, fail_silently)
