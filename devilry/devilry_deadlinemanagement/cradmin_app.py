# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_deadlinemanagement.views import multiselect_groups_view
from devilry.devilry_deadlinemanagement.views import manage_deadline_view
from devilry.devilry_deadlinemanagement.views import deadline_listview


class AbstractDeadlineManagementApp(crapp.App):
    def get_accessible_group_queryset(self, user=None):
        """
        Get QuerySet of :obj:`~.devilry.apps.core.models.AssignmentGroup` where the user has
        access.

        Returns:
            (QuerySet): Of :obj:`~.devilry.apps.core.models.AssignmentGroup`.
        """
        raise NotImplementedError()

    @classmethod
    def get_index_view_class(cls):
        return deadline_listview.DeadlineListView

    @classmethod
    def get_groups_multiselect_view_move_deadline_class(cls):
        return multiselect_groups_view.MoveDeadlineManualGroupSelectView

    @classmethod
    def get_groups_multiselect_view_new_attempt_class(cls):
        return multiselect_groups_view.NewAttemptManualGroupSelectView

    @classmethod
    def get_manage_deadline_view_single_group_class(cls):
        return manage_deadline_view.ManageDeadlineSingleGroupView

    @classmethod
    def get_manage_deadline_view_all_groups_class(cls):
        return manage_deadline_view.ManageDeadlineAllGroupsView

    @classmethod
    def get_manage_deadline_from_previous_view_class(cls):
        return manage_deadline_view.ManageDeadlineFromPreviousView

    @classmethod
    def get_appurls(cls):
        return [
            # App index view.
            crapp.Url(
                r'^$',
                cls.get_index_view_class().as_view(),
                name=crapp.INDEXVIEW_NAME
            ),

            # Multi select groups views.
            crapp.Url(
                r'select-manually-move-deadline/(?P<deadline>\w+)$',
                cls.get_groups_multiselect_view_move_deadline_class().as_view(),
                name='select-manually-move-deadline'),
            crapp.Url(
                r'select-manually-move-deadline/(?P<deadline>\w+)/(?P<filters_string>.+)?$',
                cls.get_groups_multiselect_view_move_deadline_class().as_view(),
                name='select-manually-move-deadline-filter'),
            crapp.Url(
                r'select-manually-new-attempt/(?P<deadline>\w+)$',
                cls.get_groups_multiselect_view_new_attempt_class().as_view(),
                name='select-manually-new-attempt'),
            crapp.Url(
                r'select-manually-new-attempt/(?P<deadline>\w+)/(?P<filters_string>.+)?$',
                cls.get_groups_multiselect_view_new_attempt_class().as_view(),
                name='select-manually-new-attempt-filter'),

            # Manage deadline views.
            crapp.Url(
                r'manage-deadline/(?P<handle_deadline>\w+)/(?P<group_id>\d*)$',
                cls.get_manage_deadline_view_single_group_class().as_view(),
                name='manage-deadline-single-group'),
            crapp.Url(
                r'manage-deadline/(?P<handle_deadline>\w+)/(?P<all>\w+)$',
                cls.get_manage_deadline_view_all_groups_class().as_view(),
                name='manage-deadline-all-groups'),
            crapp.Url(
                r'manage-deadline/(?P<deadline>\w+)/(?P<handle_deadline>[\w-]+)$',
                cls.get_manage_deadline_from_previous_view_class().as_view(),
                name='manage-deadline-post')
        ]


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
