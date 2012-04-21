from django.conf.urls.defaults import patterns
from restful import example_restful

urlpatterns = patterns('devilry.apps.restfulexample')
urlpatterns += example_restful
