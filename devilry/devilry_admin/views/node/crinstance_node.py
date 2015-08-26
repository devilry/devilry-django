from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.apps.core.models import Node
from devilry.devilry_admin.views.node import overview
from devilry.devilry_admin.views.node import admins


class Menu(crmenu.Menu):
    def build_menu(self):
        node = self.request.cradmin_role
        self.add_menuitem(
            label=node.short_name,
            url=self.appindex_url('overview'))
        self.add_menuitem(
            label=_('Administrators'),
            url=self.appindex_url('admins'))


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Node
    apps = [
        ('overview', overview.App),
        ('admins', admins.App),
    ]
    id = 'devilry_admin_nodeadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Node.where_is_admin_or_superadmin(self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is an Node.
        """
        node = role
        return node

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/node')
