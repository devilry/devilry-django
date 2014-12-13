# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from .nodedetails import NodeDetails
from .toplevel_node_listing import ToplevelNodeListing
from .aggregatedstudentinfo import AggregatedStudentInfo


urlpatterns = patterns('devilry.devilry_nodeadmin.rest',
    url(r'^toplevel_nodes/$', ToplevelNodeListing.as_view(),
        name='devilry_nodeadmin-rest_toplevel_nodes'),
    url(r'^node/details/(?P<id>\d+)$', NodeDetails.as_view(),
        name='devilry_nodeadmin-rest_node_details'),
    url(r'^aggregatedstudentinfo/(?P<user_id>\d+)(\.(?P<_format>[a-zA-Z]+))?$', AggregatedStudentInfo.as_view(),
        name='devilry_nodeadmin-aggregatedstudentinfo'),

)
