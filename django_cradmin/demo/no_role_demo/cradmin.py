from django.utils.translation import gettext_lazy as _

from django_cradmin import crinstance, crmenu
from django_cradmin.demo.no_role_demo.views import dashboard


class NoRoleCrAdminInstance(crinstance.NoRoleMixin, crinstance.BaseCrAdminInstance):
    id = "no_role_demo"
    rolefrontpage_appname = "dashboard"

    apps = [
        ("dashboard", dashboard.App),
    ]

    def has_access(self):
        return True

    def get_menu_item_renderables(self):
        return [
            crmenu.NavLinkItemRenderable(
                label=_("Dashboard"),
                url=self.appindex_url("dashboard"),
                is_active=self.request.cradmin_app.appname == "dashboard",
            ),
        ]
