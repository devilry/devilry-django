
# CrAdmin imports
from django_cradmin import crapp

# Devilry imports
from devilry.devilry_qualifiesforexam.views import proxyview


class PluginSelectView(proxyview.PageProxyView):
    pass


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            proxyview.PageProxyView.as_view(),
            name='select-plugin'
        )
    ]
