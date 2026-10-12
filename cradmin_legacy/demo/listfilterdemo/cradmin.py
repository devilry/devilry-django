from cradmin_legacy import crinstance, crmenu
from cradmin_legacy.demo.listfilterdemo.models import Site
from cradmin_legacy.demo.listfilterdemo.views import personlist


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add_menuitem(
            label="Personlist",
            url=self.appindex_url("personlist"),
            active=self.request.cradmin_app.appname == "personlist",
        )


class ListfilterDemoCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = "listfilterdemo"
    menuclass = Menu
    roleclass = Site
    rolefrontpage_appname = "personlist"

    apps = [
        ("personlist", personlist.App),
    ]

    def get_rolequeryset(self):
        queryset = Site.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(admins=self.request.user)
        return queryset

    def get_titletext_for_role(self, role):
        return role.name

    @classmethod
    def matches_urlpath(cls, urlpath):
        """
        We only need this because we have multiple cradmin UIs
        in the demo project.
        """
        return urlpath.startswith("/listfilterdemo")
