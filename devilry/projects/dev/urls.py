from django.contrib import admin
from django.conf.urls.defaults import patterns, include

from devilry.apps.core import pluginloader
from devilry.apps.default_urls import devilry_urls, fileserve_url

admin.autodiscover()


urlpatterns = patterns('',
    # Custom urls for this project
    (r'^guiexamples/', include('devilry.apps.guiexamples.urls')),

    # Django admin interface and login page. The admin interface is only
    # needed for user administration.
    (r'^superadmin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Include the url to serve static files (../../static) at /static/
    fileserve_url,

    # Include the urls of all devilry apps
    *devilry_urls
)


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
