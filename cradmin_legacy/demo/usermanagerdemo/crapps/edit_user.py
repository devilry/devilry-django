from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy
from crispy_forms import layout

from cradmin_legacy.crispylayouts import PrimarySubmit
from cradmin_legacy.viewhelpers import update
from cradmin_legacy import crapp


class EditUserView(update.UpdateRoleView):
    """
    View used to edit the user.
    """

    model = User
    fields = [
        "username",
        "first_name",
        "last_name",
    ]

    def get_success_message(self, object):
        return gettext_lazy("Updated your account information.")

    def get_field_layout(self):
        return [layout.Div("username", "first_name", "last_name", css_class="cradmin-globalfields")]

    def get_buttons(self):
        return [
            PrimarySubmit("submit-save", gettext_lazy("Save")),
        ]


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", EditUserView.as_view(), name=crapp.INDEXVIEW_NAME),
    ]
