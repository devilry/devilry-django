from django.conf.urls.defaults import patterns, url

from .aggregated_groupinfo import AggregatedGroupInfo


urlpatterns = patterns('devilry_student.rest',
                       url(r'^aggregated_groupinfo/(?P<id>\d+)$', AggregatedGroupInfo.as_view())
                      )
