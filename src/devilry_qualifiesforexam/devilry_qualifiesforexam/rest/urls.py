from django.conf.urls.defaults import patterns, url

from .aggregatedperiod import AggregatePeriod
from .plugins import Plugins
from .preview import Preview
from .status import StatusView


urlpatterns = patterns('devilry_qualifiesforexam.rest',
                       url(r'^aggregatedperiod/(?P<id>\d+)$', AggregatePeriod.as_view()),
                       url(r'^status$', StatusView.as_view()),
                       url(r'^plugins$', Plugins.as_view()),
                       url(r'^preview/(?P<id>\d+)$', Preview.as_view())
                      )
