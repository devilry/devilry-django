from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from devilry.settings import EMAIL_SUBJECT_PREFIX
from devilry.settings import EMAIL_DEFAULT_FROM

def send_email(user_objects_to_send_to, subject, message):
    if not SEND_EMAIL_TO_USERS:
        return
    message += "\n\n--\n"
    message += _("This is a message from the Devilry assignment delivery system. " \
                     "Please do not respond to this email.")
    emails = []

    for u in user_objects_to_send_to:
        if u.email == None or u.email.strip() == '':
            mail_admins("[devilry] Invalid email", "User %s has no email address." % u.username,
                        fail_silently=False)
        else:
            emails.append(u.email)
    try:
        send_mail(EMAIL_SUBJECT_PREFIX + subject, message, EMAIL_DEFAULT_FROM,
                  emails, fail_silently=False)
    except Exception, e:
        mail_admins("[devilry]", "Error when sending email to user %s on address %s. Exception: %s" %
                    (u.username, u.email, e),
                    fail_silently=False)
        raise
