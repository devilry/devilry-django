# Python imports
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry/cradmin imports
from django.http import Http404
from django_cradmin import crmenu
from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_group.cradmin_instances import crinstance_base
from devilry.devilry_group.views.admin import feedbackfeed_admin
from devilry.devilry_group.views.download_files import feedbackfeed_bulkfiledownload


class Menu(crmenu.Menu):
    devilryrole = 'admin'

    def build_menu(self):
        group = self.request.cradmin_role
        self.add_headeritem(
            label=group.subject.long_name,
            url=self.appindex_url('feedbackfeed'))


class AdminCrInstance(crinstance_base.CrInstanceBase):
    """
    CrInstance class for admins.
    """
    menuclass = Menu
    apps = [
        ('feedbackfeed', feedbackfeed_admin.App),
        ('feedbackfeed', feedbackfeed_bulkfiledownload.App)
    ]
    id = 'devilry_group_admin'

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/admin')

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
