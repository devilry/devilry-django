from django.utils.translation import gettext_lazy

from cradmin_legacy import crinstance, crmenu
from cradmin_legacy.demo.no_role_demo.views import dashboard


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add_menuitem(
            label=gettext_lazy("Dashboard"),
            url=self.appindex_url("dashboard"),
            active=self.request.cradmin_app.appname == "dashboard",
        )


class NoRoleCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = "no_role_demo"
    menuclass = Menu
    rolefrontpage_appname = "dashboard"
    flatten_rolefrontpage_url = True

    apps = [
        ("dashboard", dashboard.App),
    ]

    def has_access(self):
        """
        We give any user access to this instance, including unauthenticated users.
        """
        return True

    @classmethod
    def matches_urlpath(cls, urlpath):
        """
        We only need this because we have multiple cradmin UIs
        in the same project.
        """
        return urlpath.startswith("/no_role_demo")
