from django.conf.urls import patterns, url, include
from devilry.devilry_group.cradmin_feedback_feed import cradmin_feedback_feed

urlpatterns = patterns(
    'devilry.devilry_group',
    url(r'^', include(cradmin_feedback_feed.CrAdminInstance.urls()))
)