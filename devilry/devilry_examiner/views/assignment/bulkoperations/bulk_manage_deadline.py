# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_deadlinemanagement.cradmin_app import ExaminerDeadlineManagementApp
from devilry.devilry_deadlinemanagement.views import deadline_listview


class ExaminerManageDeadlineView(deadline_listview.DeadlineListView):
    def get_startapp_backlink_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_examiner_assignment',
            appname='grouplist',
            roleid=self.request.cradmin_role.id,
            viewname=crapp.INDEXVIEW_NAME
        )


class App(ExaminerDeadlineManagementApp):
    @classmethod
    def get_manage_deadline_view_single_group_class(cls):
        return ExaminerManageDeadlineView

