from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy

from cradmin_legacy import crinstance, crmenu
from .crapps import overview
from .crapps import edit_user


class Menu(crmenu.Menu):
    def build_menu(self):
        if self.request.cradmin_instance.get_rolequeryset().count() > 1:
            self.add_headeritem(label=gettext_lazy("Select user"), url=self.roleselectview_url(), icon="chevron-up")

        self.add_menuitem(
            label=gettext_lazy("Account overview"),
            url=self.appindex_url("overview"),
            active=self.request.cradmin_app.appname == "overview",
        )
        self.add_menuitem(
            label=gettext_lazy("Edit profile"),
            url=self.appindex_url("edit_user"),
            active=self.request.cradmin_app.appname == "edit_user",
        )


class UsermanagerCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = "usermanager"
    menuclass = Menu
    roleclass = User
    rolefrontpage_appname = "overview"

    apps = [
        ("overview", overview.App),
        ("edit_user", edit_user.App),
    ]

    def get_rolequeryset(self):
        queryset = User.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(id=self.request.user.id).order_by("username")
        return queryset

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role)

    @classmethod
    def matches_urlpath(cls, urlpath):
        """
        We only need this because we have multiple cradmin UIs
        in the same project.
        """
        return urlpath.startswith("/usermanagerdemo")
