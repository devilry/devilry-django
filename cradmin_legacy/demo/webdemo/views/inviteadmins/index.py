from django.utils.translation import gettext_lazy

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata
from cradmin_legacy.viewhelpers import objecttable
from .mixins import QuerysetForRoleMixin


class EmailColumn(objecttable.MultiActionColumn):
    modelfield = "id"

    def get_header(self):
        return gettext_lazy("Email")

    def get_buttons(self, obj):
        return [
            objecttable.Button(
                label=gettext_lazy("Delete"),
                url=self.reverse_appurl("delete", args=[obj.id]),
                buttonclass="btn btn-danger btn-sm",
            ),
        ]

    def render_value(self, obj):
        return obj.metadata["email"]

    def is_sortable(self):
        return False


class CreatedDatetimeColumn(objecttable.DatetimeColumn):
    modelfield = "created_datetime"

    def get_default_ordering(self):
        return None


class ExpirationDatetimeColumn(objecttable.DatetimeColumn):
    modelfield = "expiration_datetime"


class Overview(QuerysetForRoleMixin, objecttable.ObjectTableView):
    model = GenericTokenWithMetadata
    columns = [EmailColumn, CreatedDatetimeColumn, ExpirationDatetimeColumn]
    searchfields = ["metadata_json"]

    def get_no_items_message(self):
        return gettext_lazy("No pending invites. Click the button above to invite new administrators for the site.")

    def get_pagetitle(self):
        return gettext_lazy("Invite admins")

    def get_buttons(self):
        app = self.request.cradmin_app
        return [
            objecttable.Button(
                label=gettext_lazy("Send private invite"), url=app.reverse_appurl("send"), buttonclass="btn btn-primary"
            ),
        ]
