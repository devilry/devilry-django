from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView

from devilry.apps.core import pluginloader
from devilry_settings.default_urls import devilry_urls
from devilry_frontpage.views import frontpage


urlpatterns = patterns('',
    # Custom urls
    url(r'^trix/', include('trix.urls')),

    # Move the default Devilry frontpage to /devilry, and redirect to Trix instead.
    (r'^devilry/$', frontpage),
    (r'^$', RedirectView.as_view(permanent=False, url="/trix/", query_string=True)),


    # Add the default Devilry urls
    *devilry_urls
) + staticfiles_urlpatterns()

# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
