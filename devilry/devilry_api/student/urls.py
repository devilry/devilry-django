# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url, include
from devilry.devilry_api.student.views.assignment_views import (
    AssignmentGroupListView,
    AssignmentListView)

urlpatterns = [
    url('^assignmentgroup/list$', AssignmentGroupListView.as_view(), name='assignmentgroup-list'),
    url('^assignment/list/$', AssignmentListView.as_view(), name='assigment-list'),
]

