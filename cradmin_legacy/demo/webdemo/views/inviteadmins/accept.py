from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect

from cradmin_legacy.apps.cradmin_invite.baseviews.accept import AbstractAcceptInviteView


class AcceptPrivateSiteAdminInviteView(AbstractAcceptInviteView):
    # description_template_name = 'myapp/invite_description.django.html'

    def get_appname(self):
        return "webdemo_inviteadmins"

    def invite_accepted(self, generictoken):
        site = generictoken.content_object
        site.admins.add(self.request.user)
        messages.success(self.request, "You are now admin on {site}".format(site=site))
        return HttpResponseRedirect(settings.LOGIN_URL)
