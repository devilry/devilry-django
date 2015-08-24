from __future__ import unicode_literals
from django.views.generic import TemplateView

from django_cradmin import crapp


class Overview(TemplateView):
    template_name = 'devilry_admin/assignment/overview.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
