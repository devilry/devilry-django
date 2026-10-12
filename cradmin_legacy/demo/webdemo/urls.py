from django.urls import re_path

from cradmin_legacy.demo.webdemo.views.inviteadmins.accept import AcceptPrivateSiteAdminInviteView
from cradmin_legacy.demo.webdemo.views.sharable_link.accept import AcceptPublicSiteAdminInviteView

urlpatterns = [
    re_path(
        r"^inviteadmins/(?P<token>.+)$", AcceptPrivateSiteAdminInviteView.as_view(), name="webdemo-inviteadmins-accept"
    ),
    re_path(
        r"^sharable_link/(?P<token>.+)$",
        AcceptPublicSiteAdminInviteView.as_view(),
        name="webdemo-inviteadmins-public-accept",
    ),
]
