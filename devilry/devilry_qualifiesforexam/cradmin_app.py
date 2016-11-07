# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# CrAdmin imports
from django_cradmin import crapp

# Devilry imports
from .views import pluginselection_view
from .views import proxyview
from .views import qualifiesforexam_view


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
            qualifiesforexam_view.QualificationBaseView.as_view(),
            name='preview'
        )
    ]
