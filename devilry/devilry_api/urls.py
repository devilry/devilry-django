# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^assignment/', include('devilry.devilry_api.assignment.urls')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
]

urlpatterns += router.urls
