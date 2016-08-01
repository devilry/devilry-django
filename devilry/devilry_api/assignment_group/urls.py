# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url
from devilry.devilry_api.assignment_group.views.assignmentgroup_student import AssignmentGroupListViewStudent
urlpatterns = [
    url(r'^student/$', AssignmentGroupListViewStudent.as_view(), name='student-assignment-group'),
]
