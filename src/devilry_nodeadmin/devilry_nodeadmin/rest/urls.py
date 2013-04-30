# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

from .nodedetails import NodeDetails
from .toplevel_node_listing import ToplevelNodeListing


urlpatterns = patterns('devilry_nodeadmin.rest',
    url(r'^toplevel_nodes/$', ToplevelNodeListing.as_view(),
        name='devilry_nodeadmin-toplevel_nodes'),
    url(r'^node/details/(?P<pk>\d+)$', NodeDetails.as_view(),
        name='devilry_nodeadmin-node_details'),

)
