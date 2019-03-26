

from cradmin_legacy import crapp

from . import index
from . import select_language


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            index.IndexView.as_view(),
            name=crapp.INDEXVIEW_NAME
        ),
        crapp.Url(
            r'^select-language$',
            select_language.SelectLanguageView.as_view(),
            name='select_language'
        ),
    ]
