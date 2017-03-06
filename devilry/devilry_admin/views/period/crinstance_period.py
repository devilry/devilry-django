from django_cradmin import crinstance

from devilry.apps.core.models import Period
from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_admin.views.period import admins
from devilry.devilry_admin.views.period import createassignment
from devilry.devilry_admin.views.period import examiners
from devilry.devilry_admin.views.period import overview
from devilry.devilry_admin.views.period import students
from devilry.devilry_admin.views.period import edit
from devilry.devilry_admin.views.period import overview_all_results
from devilry.devilry_qualifiesforexam import cradmin_app as qualifiesforexam
from devilry.devilry_admin.views.period.manage_tags import manage_tags


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        period = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_subject_breadcrumb_item(subject=period.subject)
        self.add_period_breadcrumb_item(period=period, active=True)


class CrAdminInstance(devilry_crinstance.BaseCrInstanceAdmin):
    menuclass = Menu
    roleclass = Period
    apps = [
        ('overview', overview.App),
        ('students', students.App),
        ('examiners', examiners.App),
        ('admins', admins.App),
        ('createassignment', createassignment.App),
        ('edit', edit.App),
        ('overview_all_results', overview_all_results.App),
        ('qualifiesforexam', qualifiesforexam.App),
        ('manage_tags', manage_tags.App),
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

    def __get_devilryrole_for_requestuser(self):
        period = self.request.cradmin_role
        devilryrole = PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
            user=self.request.user,
            period=period
        )
        if devilryrole is None:
            raise ValueError('Could not find a devilryrole for request.user. This must be a bug in '
                             'get_rolequeryset().')

        return devilryrole

    def get_devilryrole_for_requestuser(self):
        """
        Get the devilryrole for the requesting user on the current
        period (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
        exept that this method raises ValueError if it does not find a role.
        """
        if not hasattr(self, '_devilryrole_for_requestuser'):
            self._devilryrole_for_requestuser = self.__get_devilryrole_for_requestuser()
        return self._devilryrole_for_requestuser
