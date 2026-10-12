from cradmin_legacy import crapp

from . import index
from . import send
from . import delete


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", index.Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^send$", send.SendInvitesView.as_view(), name="send"),
        crapp.Url(r"^delete/(?P<pk>\d+)$", delete.DeleteInvitesView.as_view(), name="delete"),
    ]
