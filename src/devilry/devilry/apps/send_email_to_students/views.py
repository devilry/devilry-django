from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import View

from devilry.utils.devilry_email import send_email


emailbodytpl = """This was sent by the superuser with username="{username}"
to test that email sending to you user works, and that
email-sending in Devilry uses the correct dataset.

Url of the Devilry frontpage:
{frontpageurl}
"""

class EmailSendingDebug(View):
    def get(self, request, username):
        if not request.user.is_superuser:
            return HttpResponseForbidden('Requires superuser')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseNotFound('User "{username}" does not exist'.format(**vars()))

        if not user.email:
            return HttpResponseBadRequest('User "{username}" has no email address'.format(**vars()))

        subject = 'Test email from Devilry.'
        body = emailbodytpl.format(username=request.user.username,
                                   frontpageurl=reverse('devilry_frontpage'))

        send_email([user], subject, body)
        return render(request, 'send_email_to_users/email_sending_debug.django.html',
                      {'email': user.email,
                       'subject': subject,
                       'body': body},
                      content_type="text/html")
