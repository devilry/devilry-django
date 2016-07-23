# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.assignment.views.assignment_student import (
    AssignmentListView,
    AssignmentView)

urlpatterns = [
    url('^student/list/$', AssignmentListView.as_view(), name='assigment-list'),
    url('^student/(?P<subject>.+)/(?P<semester>.+)/(?P<assignment>.+)/', AssignmentView.as_view(), name='assignment'),
]
