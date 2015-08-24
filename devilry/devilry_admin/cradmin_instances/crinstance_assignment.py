from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment import overview


class Menu(crmenu.Menu):
    def build_menu(self):
        assignment = self.request.cradmin_role
        self.add_headeritem(
            label=assignment.short_name,
            url=self.appindex_url('overview'))


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Assignment
    apps = [
        ('overview', overview.App)
    ]
    id = 'devilry_admin_assignmentadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Assignment.where_is_admin_or_superadmin(self.request.user)

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
