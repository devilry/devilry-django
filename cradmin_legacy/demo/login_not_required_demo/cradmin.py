from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy

from cradmin_legacy import crinstance, crmenu
from cradmin_legacy.demo.login_not_required_demo.views import dashboard
from cradmin_legacy.demo.webdemo.models import Site


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add_menuitem(
            label=gettext_lazy("Dashboard"),
            url=self.appindex_url("dashboard"),
            active=self.request.cradmin_app.appname == "dashboard",
        )


class LoginNotRequiredCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = "login_not_required_demo"
    menuclass = Menu
    roleclass = Site
    rolefrontpage_appname = "dashboard"

    apps = [
        ("dashboard", dashboard.App),
    ]

    def get_rolequeryset(self):
        """
        We do give access to all sites - further access management should
        be handled in each app/view.
        """
        queryset = Site.objects.all()
        return queryset

    def has_access(self):
        """
        We give any user access to this instance.
        """
        return True

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a Site.
        """
        return role.name

    def get_descriptiontext_for_role(self, role):
        """
        Get a short description of the given ``role``.
        Remember that the role is a Site.
        """
        return truncatechars(role.description, 100)

    @classmethod
    def matches_urlpath(cls, urlpath):
        """
        We only need this because we have multiple cradmin UIs
        in the same project.
        """
        return urlpath.startswith("/login_not_required_demo")
