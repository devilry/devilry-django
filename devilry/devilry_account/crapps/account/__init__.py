from __future__ import unicode_literals

from django_cradmin import crapp

from . import index


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  index.IndexView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]
