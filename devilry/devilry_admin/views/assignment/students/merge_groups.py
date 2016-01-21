from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy
from django_cradmin import crapp

from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder


class TargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Create project group')


class MergeGroupsView(groupview_base.BaseMultiselectView):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/students/merge_groups.django.html'

    def get_target_renderer_class(self):
        return TargetRenderer


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  MergeGroupsView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  MergeGroupsView.as_view(),
                  name='filter'),
    ]
