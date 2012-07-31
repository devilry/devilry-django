
from django.conf.urls.defaults import patterns, url

from .views import settings_view

urlpatterns = patterns('devilry_authenticateduserinfo',
                       url(r'^settings.js$', settings_view),
                      )

