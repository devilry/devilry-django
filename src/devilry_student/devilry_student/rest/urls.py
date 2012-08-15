from django.conf.urls.defaults import patterns, url

from .aggregated_groupinfo import AggregatedGroupInfo
from .add_delivery import AddDeliveryView


urlpatterns = patterns('devilry_student.rest',
                       url(r'^aggregated_groupinfo/(?P<id>\d+)$', AggregatedGroupInfo.as_view()),
                       url(r'^add-delivery/(?P<id>\d+)$', AddDeliveryView.as_view())
                      )
