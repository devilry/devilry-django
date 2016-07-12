# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from devilry.devilry_api.assignment.views import AssignmentView

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^assignments/$', AssignmentView.as_view(), name='assignments')
]

urlpatterns += router.urls