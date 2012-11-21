from django.conf.urls.defaults import patterns
#from django.conf.urls.defaults import include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from devilry.apps.core import pluginloader
from devilry_settings.default_urls import devilry_urls


urlpatterns = patterns('',
                       # Urls for apps under development
                       #(r'^devilry_subjectadmin/', include('devilry_subjectadmin.urls')),

                       # Add the default Devilry urls
                       *devilry_urls
) + staticfiles_urlpatterns()


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
