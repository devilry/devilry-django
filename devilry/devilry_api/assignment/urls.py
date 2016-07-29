# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url

from devilry.devilry_api.assignment.views.assignment_student import (
    AssignmentListView)

urlpatterns = [
    url('^student/$', AssignmentListView.as_view(), name='assigment-list')
]
