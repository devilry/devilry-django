from django_cradmin import crinstance

from devilry.apps.core.models import Assignment
from devilry.devilry_account.models import SubjectPermissionGroup, PermissionGroup, PeriodPermissionGroup
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_admin.views.assignment import overview
from devilry.devilry_admin.views.assignment.students import create_groups
from devilry.devilry_admin.views.assignment.students import overview as studentoverview
from devilry.devilry_admin.views.assignment.students import replace_groups
from devilry.devilry_admin.views.assignment.students import merge_groups


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        assignment = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_subject_breadcrumb_item(subject=assignment.subject)
        self.add_period_breadcrumb_item(period=assignment.period)
        self.add_assignment_breadcrumb_item(assignment=assignment,
                                            active=True)


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = Assignment
    apps = [
        ('overview', overview.App),
        ('studentoverview', studentoverview.App),
        ('create_groups', create_groups.App),
        ('replace_groups', replace_groups.App),
        ('merge_groups', merge_groups.App),
    ]
    id = 'devilry_admin_assignmentadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Assignment.objects.filter_user_is_admin(user=self.request.user)\
            .select_related('parentnode', 'parentnode__parentnode')\
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

    def __get_devilryrole_for_requestuser(self):
        assignment = self.request.cradmin_role
        devilryrole = PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
            user=self.request.user,
            period=assignment.period
        )
        if devilryrole is None:
            raise ValueError('Could not find a devilryrole for request.user. This must be a bug in '
                             'get_rolequeryset().')

        return devilryrole

    def get_devilryrole_for_requestuser(self):
        """
        Get the devilryrole for the requesting user on the current
        assignment (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
        exept that this method raises ValueError if it does not find a role.
        """
        if not hasattr(self, '_devilryrole_for_requestuser'):
            self._devilryrole_for_requestuser = self.__get_devilryrole_for_requestuser()
        return self._devilryrole_for_requestuser
