from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy
from cradmin_legacy import crinstance, crmenu
from cradmin_legacy.apps.cradmin_imagearchive import cradminviews as imagearchive

from cradmin_legacy.demo.webdemo.models import Site
from cradmin_legacy.demo.webdemo.views import pages_listbuilder
from cradmin_legacy.demo.webdemo.views import dashboard
from cradmin_legacy.demo.webdemo.views import pages
from cradmin_legacy.demo.webdemo.views import formutils
from cradmin_legacy.demo.webdemo.views import inviteadmins
from cradmin_legacy.demo.webdemo.views import sharable_link


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add_headeritem(label=gettext_lazy("Select role"), url=self.cradmin_instance.roleselectview_url())
        self.add_menuitem(
            label=gettext_lazy("Dashboard"),
            url=self.appindex_url("dashboard"),
            active=self.request.cradmin_app.appname == "dashboard",
        )
        self.add_menuitem(
            label=gettext_lazy("Pages"),
            url=self.appindex_url("pages"),
            active=self.request.cradmin_app.appname == "pages",
        )
        self.add_menuitem(
            label=gettext_lazy("Pages (listbuilder)"),
            url=self.appindex_url("pages_listbuilder"),
            active=self.request.cradmin_app.appname == "pages_listbuilder",
        )
        self.add_menuitem(
            label=gettext_lazy("FormUtils demo"),
            url=self.appindex_url("formutils"),
            active=self.request.cradmin_app.appname == "formutils",
        )
        self.add_menuitem(
            label=gettext_lazy("Images"),
            url=self.appindex_url("imagearchive"),
            active=self.request.cradmin_app.appname == "imagearchive",
        )

        self.add_footeritem(
            label=gettext_lazy("Invite admins"),
            url=self.appindex_url("inviteadmins"),
            active=self.request.cradmin_app.appname == "inviteadmins",
        )
        self.add_footeritem(
            label=gettext_lazy("Share"),
            url=self.appindex_url("sharable_link"),
            active=self.request.cradmin_app.appname == "sharable_link",
        )


class WebdemoCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = "webdemo"
    menuclass = Menu
    roleclass = Site
    rolefrontpage_appname = "dashboard"

    apps = [
        ("dashboard", dashboard.App),
        ("pages", pages.App),
        ("pages_listbuilder", pages_listbuilder.App),
        ("formutils", formutils.App),
        ("imagearchive", imagearchive.App),
        ("inviteadmins", inviteadmins.App),
        ("sharable_link", sharable_link.App),
    ]

    def get_rolequeryset(self):
        queryset = Site.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(admins=self.request.user)
        return queryset

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
        return urlpath.startswith("/webdemo")
