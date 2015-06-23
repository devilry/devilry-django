from devilry.apps.core.models.node import Node

from django_cradmin import crmenu, crinstance
from django.utils.translation import ugettext_lazy as _

from .crapps import listpermissionnodes


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add(label=_('List nodes'), url=self.appindex_url('listnodes_index'), icon="home",
                 active=self.request.cradmin_app.appname == 'listnodes_index')


class NodeListingCrAdminInstance(crinstance.BaseCrAdminInstance):
    id = 'nodepermission_listing'
    menuclass = Menu
    roleclass = Node
    rolefrontpage_appname = 'listnodes_index'

    apps = [
        ('listnodes_index', listpermissionnodes.App),
    ]

    def get_rolequeryset(self):
        if self.request.user.is_superuser:
            return Node.objects.all()
        return Node.objects.filter(Node.q_is_admin(self.request.user))

    def get_titletext_for_role(self, role):
        return role.short_name

    def get_descriptiontext_for_role(self, role):
        return role.long_name

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_nodeadmin/')