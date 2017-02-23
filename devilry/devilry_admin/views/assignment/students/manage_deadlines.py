# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_deadlinemanagement.cradmin_app import AdminDeadlineManagementApp
from devilry.devilry_deadlinemanagement.views import deadline_listview
from devilry.devilry_deadlinemanagement.views import manage_deadline_view


class AdminDeadlineListView(deadline_listview.DeadlineListView):
    def get_backlink_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='studentoverview',
            roleid=self.request.cradmin_instance.assignment.id,
            viewname=crapp.INDEXVIEW_NAME
        )


class AdminManageDeadlineFromPreviousView(manage_deadline_view.ManageDeadlineFromPreviousView):
    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='studentoverview',
            roleid=self.request.cradmin_instance.assignment.id,
            viewname=crapp.INDEXVIEW_NAME
        )


class App(AdminDeadlineManagementApp):
    @classmethod
    def get_index_view_class(cls):
        return AdminDeadlineListView

    @classmethod
    def get_manage_deadline_from_previous_view_class(cls):
        return AdminManageDeadlineFromPreviousView
