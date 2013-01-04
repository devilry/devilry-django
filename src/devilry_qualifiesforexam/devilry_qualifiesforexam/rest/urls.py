from django.conf.urls.defaults import patterns, url

from .aggregatedperiod import AggregatePeriod
from .plugins import Plugins


urlpatterns = patterns('devilry_qualifiesforexam.rest',
                       url(r'^aggregatedperiod/(?P<id>\d+)$', AggregatePeriod.as_view()),
                       url(r'^plugins$', Plugins.as_view())
                      )
