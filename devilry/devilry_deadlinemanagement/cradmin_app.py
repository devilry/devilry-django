# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_deadlinemanagement.views import multiselect_groups_view
from devilry.devilry_deadlinemanagement.views import manage_deadline_view


class AbstractDeadlineManagementApp(crapp.App):
    deadline_appurls = [
        crapp.Url(r'choose-manually/(?P<deadline>\w+)$',
                  multiselect_groups_view.BulkManageDeadlineMultiSelectView.as_view(),
                  name='choose-manually'),
        crapp.Url(r'choose-manually/(?P<deadline>\w+)/(?P<filters_string>.+)?$',
                  multiselect_groups_view.BulkManageDeadlineMultiSelectView.as_view(),
                  name='choose-manually-filter'),
        crapp.Url(r'manage-deadline/(?P<pk>\d*)$',
                  manage_deadline_view.ManageDeadlineView.as_view(),
                  name='manage-deadline'),
        crapp.Url(r'manage-deadline$',
                  manage_deadline_view.ManageDeadlineView.as_view(),
                  name='manage-deadline-post')
    ]

    def __init__(self, appname, request, active_viewname):
        self.appurls.extend(self.deadline_appurls)
        super(AbstractDeadlineManagementApp, self).__init__(appname, request, active_viewname)

    def get_accessible_group_queryset(self, user=None):
        """
        Get QuerySet of :obj:`~.devilry.apps.core.models.AssignmentGroup` where the user has
        access.

        Returns:
            (QuerySet): Of :obj:`~.devilry.apps.core.models.AssignmentGroup`.
        """
        raise NotImplementedError()

    @classmethod
    def get_appurls(cls):
        cls.appurls.extend(cls.deadline_appurls)
        return cls.appurls


class AdminDeadlineManagementApp(AbstractDeadlineManagementApp):
    """
    Abstract baseclass for ``Admins``.
    """
    def get_devilryrole(self):
        return 'admin'

    def get_accessible_group_queryset(self, user=None):
        user = user or self.request.user
        return AssignmentGroup.objects.filter_user_is_admin(user=user)


class ExaminerDeadlineManagementApp(AbstractDeadlineManagementApp):
    """
    Abstract baseclass for ``Examiners``.
    """
    def get_devilryrole(self):
        return 'examiner'

    def get_accessible_group_queryset(self, user=None):
        user = user or self.request.user
        return AssignmentGroup.objects.filter_examiner_has_access(user=user)
