# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_deadlinemanagement.cradmin_app import ExaminerDeadlineManagementApp
from devilry.devilry_deadlinemanagement.views import deadline_listview
from devilry.devilry_deadlinemanagement.views import manage_deadline_view


class ExaminerDeadlineListView(deadline_listview.DeadlineListView):
    def get_backlink_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_examiner_assignment',
            appname='grouplist',
            roleid=self.request.cradmin_role.id,
            viewname=crapp.INDEXVIEW_NAME
        )


class ExaminerManageDeadlineFromPreviousView(manage_deadline_view.ManageDeadlineFromPreviousView):
    """
    """


class App(ExaminerDeadlineManagementApp):
    @classmethod
    def get_index_view_class(cls):
        return ExaminerDeadlineListView

    @classmethod
    def get_manage_deadline_from_previous_view_class(cls):
        return ExaminerManageDeadlineFromPreviousView
