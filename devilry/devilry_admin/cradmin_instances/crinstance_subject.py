from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.apps.core.models import Subject
from devilry.devilry_admin.views.subject import overview


class Menu(crmenu.Menu):
    def build_menu(self):
        subject = self.request.cradmin_role
        self.add_headeritem(
            label=subject.short_name,
            url=self.appindex_url('overview'))


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Subject
    apps = [
        ('overview', overview.App)
    ]
    id = 'devilry_admin_subjectadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Subject.where_is_admin_or_superadmin(self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is an Subject.
        """
        subject = role
        return subject

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/subject')
