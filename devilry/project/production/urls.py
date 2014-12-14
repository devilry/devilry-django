from django.conf.urls import patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from devilry.apps.core import pluginloader
from devilry.project.common.default_urls import devilry_urls


urlpatterns = patterns('',
                       # Add the default Devilry urls
                       *devilry_urls
) + staticfiles_urlpatterns()

# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
