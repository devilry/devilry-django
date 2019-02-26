# -*- coding: utf-8 -*-


from django.http import Http404

from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_group.cradmin_instances import crinstance_base
from devilry.devilry_group.views.admin import feedbackfeed_admin
from devilry.devilry_group.views.download_files import batch_download_files
from devilry.devilry_group.views.admin import manage_deadline, group_comment_history


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        group = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_subject_breadcrumb_item(subject=group.assignment.subject)
        self.add_period_breadcrumb_item(period=group.assignment.period)
        self.add_assignment_breadcrumb_item(assignment=group.assignment)
        self.add_group_breadcrumb_item(group=group, active=True)


class AdminCrInstance(crinstance_base.DevilryGroupCrInstanceMixin, devilry_crinstance.BaseCrInstanceAdmin):
    """
    CrInstance class for admins.
    """
    menuclass = Menu
    apps = [
        ('feedbackfeed', feedbackfeed_admin.App),
        ('download', batch_download_files.App),
        ('commenthistory', group_comment_history.App),
        ('manage-deadline', manage_deadline.App)
    ]
    id = 'devilry_group_admin'

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/admin')

    @property
    def assignment(self):
        return self.request.cradmin_role.parentnode

    def get_rolequeryset(self):
        """
        Get the base rolequeryset from
        :meth:`~devilry.devilry_group.cradmin_instances.CrInstanceBase._get_base_rolequeryset` and filter on user.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.AssignmentGroup`s
                the ``request.user`` is admin on.
        """
        return self._get_base_rolequeryset()\
            .filter_user_is_admin(user=self.request.user)

    def __get_devilryrole_for_requestuser(self):
        """
        Checks the permission for the user via :class:`~devilry.devilry_account.models.PeriodPermissionGroup`.

        Returns:
            str: ``departmentadmin``, ``subjectadmin`` or ``periodadmin`` as devilryrole.

        Raises:
            Http404: raised when user is not admin associated with this course.
        """
        assignment = self.request.cradmin_role.assignment
        devilryrole = PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
            user=self.request.user,
            period=assignment.period
        )
        if devilryrole is None:
            raise Http404
        return devilryrole

    def get_devilryrole_for_requestuser(self):
        """
        Get the role of the user.

        Returns:
            str: ``departmentadmin``, ``subjectadmin`` or ``periodadmin`` as devilryrole.
        """
        if not hasattr(self, '_devilryrole_for_requestuser'):
            self._devilryrole_for_requestuser = self.__get_devilryrole_for_requestuser()
        return self._devilryrole_for_requestuser
