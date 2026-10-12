from django.utils.translation import gettext_lazy

from cradmin_legacy.viewhelpers import delete
from cradmin_legacy.demo.webdemo.views.sharable_link.mixins import QuerysetForRoleMixin


class DeletePublicInviteView(QuerysetForRoleMixin, delete.DeleteView):
    """
    View used to delete existing invites.
    """

    def get_action_label(self):
        return gettext_lazy("Disable")

    def get_confirm_message(self):
        return gettext_lazy("Are you sure you want to disable the sharable link?")

    def get_object_preview(self):
        return gettext_lazy("sharable link")

    def get_success_message(self, object_preview):
        return gettext_lazy("Disabled the sharable link")
