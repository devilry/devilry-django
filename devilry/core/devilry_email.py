from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from devilry.settings import email_subject_prefix

def send_email(user, subject, message):
    message += "\n\n"
    message += _("This is a message from the Devilry assignment delivery system. " \
                     "Please do not respond to this email.")
    send_mail(email_subject_prefix + subject, message, 'devilry@example.com',
              [user.email], fail_silently=False)

        
        

