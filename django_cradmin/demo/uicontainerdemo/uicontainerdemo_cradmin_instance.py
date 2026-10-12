from django_cradmin import crinstance, crmenu
from django_cradmin.demo.uicontainerdemo.crapps import uiforms_demoapp
from django_cradmin.demo.uicontainerdemo.crapps import uicontainer_overview_app


class UIContainerDemoCrAdminInstance(crinstance.NoRoleNoLoginCrAdminInstance):
    id = "uicontainerdemo"
    rolefrontpage_appname = "overview"
    flatten_rolefrontpage_url = True

    apps = [
        ("overview", uicontainer_overview_app.App),
        ("forms", uiforms_demoapp.App),
    ]

    def get_titletext_for_role(self, role):
        return "uicontainer demos"

    def get_menu_item_renderables(self):
        return [
            crmenu.NavLinkItemRenderable(
                label="Forms", url=self.appindex_url("forms"), is_active=self.request.cradmin_app.appname == "forms"
            ),
        ]
