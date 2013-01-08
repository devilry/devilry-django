# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from devilry_nodeadmin.util import emptyview
from views import *


urlpatterns = \
patterns('devilry_nodeadmin.rest',
    url( r'^$', emptyview ),
    # default view, lists all related nodes: nodes that a user administers
    url( r'^nodes/$', RelatedNodes.as_view() ),
    # navigation, lists node data and subsequent children
    url( r'^node/(?P<pk>\d+)/details$', RelatedNodeDetails.as_view() ),
    url( r'^node/(?P<parentnode__pk>\d+)/children$', RelatedNodeChildren.as_view() )

)
