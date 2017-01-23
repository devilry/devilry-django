from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp

from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class MergeGroupsTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Create project group')


class MergeGroupsView(groupview_base.BaseMultiselectView):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/students/merge_groups.django.html'

    def add_filterlist_items(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.StatusSelectFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerCountFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def get_target_renderer_class(self):
        return MergeGroupsTargetRenderer

    def form_valid(self, form):
        print(self.request.post)
        print(form.clean_data)
        messages.warning(
            self.request,
            'Merge groups is not finished')
        return redirect(self.request.get_full_path())


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  MergeGroupsView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  MergeGroupsView.as_view(),
                  name='filter'),
    ]
