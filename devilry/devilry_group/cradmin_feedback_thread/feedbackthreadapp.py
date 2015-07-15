from django_cradmin import crapp


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            #add someview.as_view()
            name=crapp.INDEXVIEW_NAME),
    ]