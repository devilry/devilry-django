from django.conf.urls import patterns

from .restful import administrator_restful

urlpatterns = patterns('devilry.apps.administrator')
urlpatterns += administrator_restful
