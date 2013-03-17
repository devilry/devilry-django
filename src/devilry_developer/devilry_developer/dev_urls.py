from django.conf.urls import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from devilry.apps.core import pluginloader
from devilry_settings.default_urls import devilry_urls


urlpatterns = patterns('',
    # Urls for apps under development
#    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^devilry_sandbox/', include('devilry_sandbox.urls')),
    (r'^devilry_qualifiesforexam/', include('devilry_qualifiesforexam.urls')),
    (r'^devilry_qualifiesforexam_approved/', include('devilry_qualifiesforexam_approved.urls')),
    (r'^devilry_qualifiesforexam_points/', include('devilry_qualifiesforexam_points.urls')),

    # Add the default Devilry urls
    *devilry_urls
) + staticfiles_urlpatterns()


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
