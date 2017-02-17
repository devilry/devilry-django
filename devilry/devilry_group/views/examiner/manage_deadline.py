# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.devilry_deadlinemanagement.cradmin_app import ExaminerDeadlineManagementApp
from devilry.devilry_deadlinemanagement.views import manage_deadline_view


# class ManageDeadlineView(manage_deadline_view.ManageDeadlineView):
#     def get_previous_view_url(self):
#         return self.request.cradmin_instance.get_instance_frontpage_url()


class App(ExaminerDeadlineManagementApp):
    """
    Overrided to get URLs with cradmin_app addons.
    """