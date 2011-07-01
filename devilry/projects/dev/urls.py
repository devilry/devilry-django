from django.conf.urls.defaults import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from devilry.apps.core import pluginloader
from devilry.apps.default_urls import devilry_urls


urlpatterns = patterns('',
                       # Custom urls for this project
                       (r'^tutorialstats/', include('devilry.projects.dev.tutorialstats.urls')),
                       *devilry_urls
) + staticfiles_urlpatterns()

# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
