from django_cradmin import crapp

from . import uicontainer_overview


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", uicontainer_overview.UiFormsOverview.as_view(), name=crapp.INDEXVIEW_NAME),
    ]
