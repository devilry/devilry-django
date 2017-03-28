import debug_toolbar
from django.conf.urls import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from devilry.apps.core import pluginloader
from devilry.project.common.default_urls import devilry_urls


urlpatterns = patterns(
    '',
    url(r'^__debug__/', include(debug_toolbar.urls)),
    # Urls for apps under development
    #url(r'^rosetta/', include('rosetta.urls')),
    url(r'^devilry_sandbox/', include('devilry.devilry_sandbox.urls')),

    ## For Trix-development
    #(r'^trix/', include('trix.urls')),

    # Testing bulk-user-creation
    (r'^devilry_bulkcreate_users/', include('devilry.devilry_bulkcreate_users.urls')),

    # Add the default Devilry urls
    *devilry_urls
) + staticfiles_urlpatterns()


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
