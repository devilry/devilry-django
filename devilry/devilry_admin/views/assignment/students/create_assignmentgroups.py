from django.views.generic import TemplateView
from django_cradmin import crapp


class Overview(TemplateView):
    template_name = 'devilry_admin/assignment/students/create_assignmentgroups/overview.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
