from django.conf.urls.defaults import patterns
from devilry.apps.jsapp.views import create_lib_urls

urlpatterns = patterns('devilry.apps.themebase',
                       *create_lib_urls(appname='themebase',
                                       libs=['jsapp']))
