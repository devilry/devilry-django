from django.conf.urls.defaults import patterns
from devilry.apps.jsapp.views import create_jasmine_url

urlpatterns = patterns('devilry.apps.themebase',
                       create_jasmine_url('themebase', libs=['jsapp'], apptype='lib'))
