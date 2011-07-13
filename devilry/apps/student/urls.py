from django.conf.urls.defaults import patterns

from restful import student_restful

urlpatterns = patterns('devilry.apps.student')
urlpatterns += student_restful
