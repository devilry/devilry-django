from cradmin_legacy import crinstance, crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from django.http import Http404

from devilry.apps.core.models import Period, Assignment
from devilry.devilry_account.models import PeriodPermissionGroup, PermissionGroup
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_cradmin import devilry_crmenu
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

    def add_subject_breadcrumb_item(self, subject, active=False):
        if self.cradmin_instance.get_devilryrole_for_requestuser() == 'periodadmin':
            return self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
                label=subject.short_name,
                url=reverse_cradmin_url(
                    instanceid='devilry_admin_subject_for_periodadmin',
                    appname='overview',
                    roleid=subject.id,
                    viewname=crapp.INDEXVIEW_NAME
                ),
                active=active
            ))
        else:
            return self.add_headeritem_object(devilry_crmenu.BreadcrumbMenuItem(
                label=subject.short_name,
                url=reverse_cradmin_url(
                    instanceid='devilry_admin_subjectadmin',
                    appname='overview',
                    roleid=subject.id,
                    viewname=crapp.INDEXVIEW_NAME
                ),
                active=active
            ))


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

    def __get_devilryrole_for_requestuser(self, period=None):
        period = period or self.request.cradmin_role
        devilryrole = PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
            user=self.request.user,
            period=period
        )
        if devilryrole is None:
            raise ValueError('Could not find a devilryrole for request.user. This must be a bug in '
                             'get_rolequeryset().')

        return devilryrole

    def get_devilryrole_for_requestuser(self, period=None):
        """
        Get the devilryrole for the requesting user on the current
        period (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
        exept that this method raises ValueError if it does not find a role.
        """
        if not hasattr(self, '_devilryrole_for_requestuser'):
            self._devilryrole_for_requestuser = self.__get_devilryrole_for_requestuser(period=period)
        return self._devilryrole_for_requestuser

    def period_admin_access_semi_anonymous_assignments_restricted(self, period=None):
        """
        Check if an admin should be restricted access to due being a
        period-admin only and the period has one or more semi-anonymous
        assignments

        This method can be used to check whether access should be restricted for
        some elements, e.g. in a view or a template.

        Returns:
            (bool): ``True`` if access should be restriced, else ``False``.
        """
        devilryrole = self.get_devilryrole_for_requestuser(period=period)
        period = period or self.request.cradmin_role
        semi_anonymous_assignments_exist = Assignment.objects\
            .filter(parentnode=period)\
            .filter(anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)\
            .exists()
        if semi_anonymous_assignments_exist and devilryrole == PermissionGroup.GROUPTYPE_PERIODADMIN:
            return True
        return False

    def get_role_from_rolequeryset(self, role):
        """
        Overriden to check if the requestuser has access to specific apps using this
        CrAdmin-instance if the requestuser is a period-admin and the period has any
        semi-anonymous assignments.
        """
        role = super().get_role_from_rolequeryset(role=role)

        requesting_appname = self.request.cradmin_app.appname
        if requesting_appname in ['qualifiesforexam', 'overview_all_results']:
            if self.period_admin_access_semi_anonymous_assignments_restricted(period=role):
                raise Http404()

        return role
