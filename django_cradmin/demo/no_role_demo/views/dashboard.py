from django_cradmin import crapp
from django_cradmin import viewhelpers


class DashboardView(viewhelpers.generic.WithinRoleTemplateView):
    template_name = "no_role_demo/dashboard.django.html"


class App(crapp.App):
    appurls = [crapp.Url(r"^$", DashboardView.as_view(), name=crapp.INDEXVIEW_NAME)]
