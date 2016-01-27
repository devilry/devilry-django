from __future__ import unicode_literals

from django.views.generic import TemplateView
from django_cradmin import crapp


class SelectMethodView(TemplateView):
    template_name = 'devilry_admin/assignment/examiners/bulk_organize.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  SelectMethodView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]
