# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.assignment.views.assignment_student import AssignmentListView as StudentAssignmentListView
from devilry.devilry_api.assignment.views.assignment_examiner import AssignmentListView as ExaminerAssignmentListView
from devilry.devilry_api.assignment.views.assignment_period_admin import PeriodAdminAssignmentView
urlpatterns = [
    url('^student/$', StudentAssignmentListView.as_view(), name='student-assigment'),
    url('^examiner/$', ExaminerAssignmentListView.as_view(), name='examiner-assignment'),
    url('^period-admin/$', PeriodAdminAssignmentView.as_view(), name='period-admin-assignment'),
]
