from django_cradmin import crmenu

from django_cradmin import crinstance

from devilry.apps.core.models import Period
from devilry.devilry_admin.views.period import overview


class Menu(crmenu.Menu):
    def build_menu(self):
        period = self.request.cradmin_role
        self.add_headeritem(
            label=period.short_name,
            url=self.appindex_url('overview'))


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Period
    apps = [
        ('overview', overview.App)
    ]
    id = 'devilry_admin_periodadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Period.where_is_admin_or_superadmin(self.request.user)\
            .order_by('-start_time')

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is an Period.
        """
        period = role
        return period

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/period')
