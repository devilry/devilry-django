# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^student/', include('devilry.devilry_api.student.urls')),
]

urlpatterns += router.urls
