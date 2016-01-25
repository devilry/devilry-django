from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
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
    def get(self, request, pk):
        if not request.user.is_superuser:
            return HttpResponseForbidden('Requires superuser')
        try:
            user = get_user_model().objects.get(pk=pk)
        except get_user_model().DoesNotExist:
            return HttpResponseNotFound('ERROR: User "#{}" does not exist'.format(pk))

        if not request.user.useremail_set.exists():
            return HttpResponseBadRequest('ERROR: YOU ({user}) have no email address'.format(
                user=request.user))
        if not user.useremail_set.exists():
            return HttpResponseBadRequest('ERROR: User "{user}" has no email address'.format(
                user=user))

        subject = 'Test email from Devilry.'
        body = emailbodytpl.format(username=request.user.shortname,
                                   frontpageurl=create_absolute_url('/'),
                                   superuseremail=request.user.useremail_set.first().email)

        send_message(subject, body, user)
        return render(request, 'send_email_to_users/email_sending_debug.django.html',
                      {'email': user.useremail_set.first().email,
                       'subject': subject,
                       'body': body},
                      content_type="text/html")
