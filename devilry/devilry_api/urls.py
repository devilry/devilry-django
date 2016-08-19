# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^assignment/', include('devilry.devilry_api.assignment.urls')),
    url(r'^assignment-group/', include('devilry.devilry_api.assignment_group.urls')),
    url(r'^feedbackset/', include('devilry.devilry_api.feedbackset.urls')),
    url(r'^group-comment/', include('devilry.devilry_api.group_comment.urls')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
]

urlpatterns += router.urls
