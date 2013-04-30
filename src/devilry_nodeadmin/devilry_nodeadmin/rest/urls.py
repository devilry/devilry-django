# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from views import RelatedNodes
from views import RelatedNodeDetails
from views import RelatedNodeChildren
from views import Path


urlpatterns = patterns('devilry_nodeadmin.rest',
    # default view, lists all related nodes: nodes that a user administers
    url( r'^nodes/$', RelatedNodes.as_view() ),
    # navigation, lists node data and subsequent children
    url( r'^node/details/(?P<pk>\d+)$', RelatedNodeDetails.as_view() ),
    url( r'^node/(?P<parentnode__pk>\d+)/children$', RelatedNodeChildren.as_view() ),
    url( r'^node/(?P<pk>\d+)/path$', Path.as_view() ),

)
