from django.conf.urls.defaults import patterns, url

from .aggregatedperiod import AggregatePeriod
from .plugins import Plugins
from .preview import Preview
from .status import StatusView
from .adminsummary import AdminSummaryResource


urlpatterns = patterns('devilry_qualifiesforexam.rest',
    url(r'^aggregatedperiod/(?P<id>\d+)$', AggregatePeriod.as_view()),
    url(r'^status/(?P<id>\d+)?$', StatusView.as_view(),
        name='devilry_qualifiesforexam-rest-status'),
    url(r'^plugins$', Plugins.as_view(),
        name='devilry_qualifiesforexam-rest-plugins'),
    url(r'^preview/(?P<id>\d+)$', Preview.as_view(),
        name='devilry_qualifiesforexam-rest-preview'),
    url(r'^adminsummary/(?P<node_id>\d+)?$', AdminSummaryResource.as_view(),
        name='devilry_qualifiesforexam-adminsummary')
)
