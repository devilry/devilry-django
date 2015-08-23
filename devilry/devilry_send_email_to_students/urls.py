from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url

from devilry.devilry_send_email_to_students.views import EmailSendingDebug

urlpatterns = patterns(
    '',
    url(r'^email_sending_debug/(?P<pk>.*\d+.*)$',
        login_required(EmailSendingDebug.as_view()),
        name='send_email_to_students_email_sending_debug')
)
