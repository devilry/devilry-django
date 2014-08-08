from django.conf.urls import patterns

from .restful import examiner_restful

urlpatterns = patterns('devilry.apps.examiner')
urlpatterns += examiner_restful
