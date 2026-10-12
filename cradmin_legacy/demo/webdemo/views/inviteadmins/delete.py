from django.template import defaultfilters

from cradmin_legacy.viewhelpers import delete
from .mixins import QuerysetForRoleMixin


class DeleteInvitesView(QuerysetForRoleMixin, delete.DeleteView):
    """
    View used to delete existing invites.
    """

    def get_object_preview(self):
        generictoken = self.get_object()
        return "{} - {}".format(
            generictoken.metadata["email"], defaultfilters.date(generictoken.created_datetime, "DATETIME_FORMAT")
        )
