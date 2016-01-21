from __future__ import unicode_literals

from django_cradmin import crapp

from devilry.devilry_admin.views.assignment.students import groupview_base


class Overview(groupview_base.BaseInfoView):
    filterview_name = 'filter'
    # template_name = 'devilry_admin/assignment/students/overview.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  Overview.as_view(),
                  name='filter'),
    ]
