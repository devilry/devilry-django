# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# CrAdmin imports
from django_cradmin import crapp

# Devilry imports
from .views import pluginselection_view
from .views import proxyview
from .views import qualification_preview_view


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            pluginselection_view.SelectPluginView.as_view(),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^configure-plugin/(?P<plugintypeid>[a-z0-9._]+)$',
            proxyview.PluginProxyView.as_view(),
            name='configure-plugin'
        ),
        crapp.Url(
            r'preview$',
            qualification_preview_view.QualificationPreviewView.as_view(),
            name='preview'
        ),
        crapp.Url(
            r'showstatus$',
            qualification_preview_view.QualificationStatusPreview.as_view(),
            name='show-status'
        ),
        crapp.Url(
            r'^retract-status/(?P<pk>\d+)$',
            qualification_preview_view.StatusRetractView.as_view(),
            name='retract-status'),
    ]
