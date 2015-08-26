from django_cradmin import crmenu
from django_cradmin import crinstance
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment import overview
from devilry.devilry_admin.views.assignment import admins


class Menu(crmenu.Menu):
    def build_menu(self):
        assignment = self.request.cradmin_role
        self.add_menuitem(
            label=assignment.short_name,
            url=self.appindex_url('overview'))
        self.add_menuitem(
            label=_('Administrators'),
            url=self.appindex_url('admins'))


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Assignment
    apps = [
        ('overview', overview.App),
        ('admins', admins.App),
    ]
    id = 'devilry_admin_assignmentadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Assignment.where_is_admin_or_superadmin(self.request.user)\
            .order_by('-publishing_time')

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is an Assignment.
        """
        assignment = role
        return assignment

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/assignment')
