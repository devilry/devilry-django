from django.conf.urls import patterns, url, include

from devilry.devilry_group import cradmin

urlpatterns = patterns(
    'devilry.devilry_group',
    url(r'^', include(cradmin.CrAdminInstance.urls()))
)