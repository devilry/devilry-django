from django_cradmin import crapp

from . import uiforms_overview
from . import simple_uiforms
from . import complex_uiforms


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", uiforms_overview.UiFormsOverview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^simple$", simple_uiforms.SimpleUiFormsView.as_view(), name="simple"),
        crapp.Url(r"^complex$", complex_uiforms.ComplextUiFormsView.as_view(), name="complex"),
    ]
