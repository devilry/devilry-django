# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_manage_deadline
from devilry.devilry_deadlinemanagement.cradmin_app import ExaminerDeadlineManagementApp
from devilry.devilry_deadlinemanagement.views import manage_deadline_view


class ManageDeadlineView(manage_deadline_view.ManageDeadlineView):
    def get_success_url(self):
        return self.cradmin_app.reverse_appurl(
            viewname=crapp.INDEXVIEW_NAME
        )


class App(ExaminerDeadlineManagementApp):
    """
    Overrided to get URLs with cradmin_app addons.
    """
    @classmethod
    def get_manage_deadline_view_single_group_class(cls):
        return bulk_manage_deadline.ExaminerManageDeadlineSingleGroup
