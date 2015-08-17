from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.views import feedbackfeed_admin


class Menu(crmenu.Menu):
    def build_menu(self):
        group = self.request.cradmin_role
        self.add_headeritem(
            label=group.subject.long_name,
            url=self.appindex_url('feedbackfeed'))


class AdminCrInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = AssignmentGroup
    apps = [
        ('feedbackfeed', feedbackfeed_admin.App)
    ]
    id = 'devilry_group_admin'
    rolefrontpage_appname = 'feedbackfeed'

    def get_rolequeryset(self):
        return AssignmentGroup.where_is_admin_or_superadmin(self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is an AssignmentGroup.
        """
        return "{} - {}".format(role.period, role.assignment.short_name)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/admin')
