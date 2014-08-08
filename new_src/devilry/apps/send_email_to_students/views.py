from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import View

from devilry.utils.devilry_email import send_message
from devilry.utils.create_absolute_url import create_absolute_url


emailbodytpl = """This was sent by the superuser with username="{username}"
to test that email sending to your user works.

## Url of the Devilry frontpage:
{frontpageurl}
If the frontpage URL is not an absolute URL, or if it is incorrect, Devilry is
not configured correctly.

## Please confirm
Please send an email to {superuseremail} and inform them that you got this
email, and if the frontpage URL is correct.
"""


class EmailSendingDebug(View):
    def get(self, request, username):
        if not request.user.is_superuser:
            return HttpResponseForbidden('Requires superuser')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseNotFound('ERROR: User "{username}" does not exist'.format(**vars()))

        if not request.user.email:
            return HttpResponseBadRequest('ERROR: YOU ({username}) have no email address'.format(username=request.user.username))
        if not user.email:
            return HttpResponseBadRequest('ERROR: User "{username}" has no email address'.format(**vars()))

        subject = 'Test email from Devilry.'
        body = emailbodytpl.format(username=request.user.username,
                                   frontpageurl=create_absolute_url(reverse('devilry_frontpage')),
                                   superuseremail=request.user.email)

        send_message(subject, body, user)
        return render(request, 'send_email_to_users/email_sending_debug.django.html',
                      {'email': user.email,
                       'subject': subject,
                       'body': body},
                      content_type="text/html")
