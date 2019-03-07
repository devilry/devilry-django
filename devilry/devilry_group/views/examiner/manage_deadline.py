# -*- coding: utf-8 -*-


from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url

from devilry.devilry_deadlinemanagement.cradmin_app import ExaminerDeadlineManagementApp
from devilry.devilry_deadlinemanagement.views import manage_deadline_view


class ManageDeadlineView(manage_deadline_view.ManageDeadlineSingleGroupView):
    def get_success_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_examiner',
            appname='feedbackfeed',
            roleid=self.kwargs.get('group_id'),
            viewname=crapp.INDEXVIEW_NAME
        )

    def get_backlink_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_examiner',
            appname='feedbackfeed',
            roleid=self.kwargs.get('group_id'),
            viewname=crapp.INDEXVIEW_NAME
        )


class App(ExaminerDeadlineManagementApp):
    """
    Override to get URLs with cradmin_app addons.
    """
    @classmethod
    def get_manage_deadline_view_single_group_class(cls):
        return ManageDeadlineView
