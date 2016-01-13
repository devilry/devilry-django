from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.apps.core.models import Period
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_admin.views.period import overview
from devilry.devilry_admin.views.period import students
from devilry.devilry_admin.views.period import examiners
from devilry.devilry_admin.views.period import admins
from devilry.devilry_admin.views.period import createassignment
from devilry.devilry_admin.views.period import qualifiedforfinalexams


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        period = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_subject_breadcrumb_item(subject=period.subject)
        self.add_period_breadcrumb_item(period=period, active=True)


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Period
    apps = [
        ('overview', overview.App),
        ('students', students.App),
        ('examiners', examiners.App),
        ('admins', admins.App),
        ('createassignment', createassignment.App),
        ('qualifiedforfinalexams', qualifiedforfinalexams.App),
    ]
    id = 'devilry_admin_periodadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Period.objects.filter_user_is_admin(user=self.request.user)\
            .order_by('-start_time')

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is n Period.
        """
        period = role
        return period

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/period')
