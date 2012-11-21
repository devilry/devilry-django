from django.conf.urls.defaults import patterns, url

from .aggregatedperiod import AggregatePeriod


urlpatterns = patterns('devilry_qualifiesforexam.rest',
                       url(r'^aggregatedperiod/(?P<id>\d+)$', AggregatePeriod.as_view())
                      )
