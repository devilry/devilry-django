from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from devilry.settings import EMAIL_SUBJECT_PREFIX
from devilry.settings import EMAIL_DEFAULT_FROM

def send_email(user_objects_to_send_to, subject, message):
    message += "\n\n--\n"
    message += _("This is a message from the Devilry assignment delivery system. " \
                     "Please do not respond to this email.")
    emails = []
    for u in user_objects_to_send_to:
        emails.append(u.email)
    send_mail(EMAIL_SUBJECT_PREFIX + subject, message, EMAIL_DEFAULT_FROM,
             emails, fail_silently=False)

        
        

