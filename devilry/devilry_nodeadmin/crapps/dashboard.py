from django.views.generic import TemplateView

from django_cradmin import crapp


class DashboardView(TemplateView):
    template_name = 'devilry_nodeadmin/dashboard.django.html'

class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', DashboardView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]