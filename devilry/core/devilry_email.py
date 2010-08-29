from django.core.mail import send_mail


class DevilryEmail(object):
    
    def __init__(self):
        self.subject_prefix = '[devilry] '
    
    def send_email(self, user, subject, message):
        
        message += "\n\nThis is a message from Devilry delivery system."
        
        send_mail(self.subject_prefix + subject, message, 'devilry@example.com',
                  [user.email], fail_silently=False)

        
        

