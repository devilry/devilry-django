# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from devilry_nodeadmin.util import emptyview
from views import *


urlpatterns = \
patterns('devilry_nodeadmin.rest',
    url( r'^$', emptyview ),
    url( r'^nodes/$', RelatedNodes.as_view() ),
    # navigation
    url( r'^node/(?P<parentnode__pk>\d+)$', RelatedNodeChildren.as_view() ),
    url( r'^node/(?P<pk>\d+)/details$', RelatedNodeDetails.as_view() )
)
