from django.conf.urls import patterns, url, include
from devilry.devilry_group.cradmin_feedback_feed import cradmin_feedback_thread

urlpatterns = patterns(
    'devilry.devilry_student',
    url(r'^', include(cradmin_feedback_thread.CrAdminInstance.urls()))
)