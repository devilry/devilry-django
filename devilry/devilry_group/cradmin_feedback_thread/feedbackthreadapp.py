from django_cradmin import crapp


#add SomeView here

class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            #add SomeView.as_view()
            name=crapp.INDEXVIEW_NAME),
    ]