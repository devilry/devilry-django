from extjs4.views import Extjs4AppView


class AppView(Extjs4AppView):
    template_name = "devilry_header/app.django.html"
    appname = 'devilry_header'
    title = 'Devilry Header - just to make the header app build'
