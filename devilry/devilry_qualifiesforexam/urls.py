# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.conf.urls import url, include

# Devilry imports
from devilry.devilry_qualifiesforexam.cradmin_instances import crinstance


urlpatterns = [
    url(r'^', include(crinstance.CrInstance.urls())),
]
