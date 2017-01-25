from __future__ import unicode_literals

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class MergeGroupsTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Create project group')


class MergeGroupsView(groupview_base.BaseMultiselectView):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/students/merge_groups.django.html'

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appurl(
            'filter', kwargs={'filters_string': self.get_filters_string()}
        )

    def add_filterlist_items(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.StatusSelectFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerCountFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.CandidateCountFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def get_target_renderer_class(self):
        return MergeGroupsTargetRenderer

    def __get_merged_candidates_short_name(self, group_queryset):
        candidates = Candidate.objects.filter(assignment_group__in=group_queryset)\
            .select_related('relatedstudent__user')
        ret = ""
        for candidate in candidates:
            ret += ", {}".format(candidate.relatedstudent.user.shortname)
        return ret[2:]

    def __get_groups_from_form(self, form):
        target_group_id = self.request.POST.getlist('selected_items')[0]
        target_group = form.cleaned_data['selected_items'].get(id=target_group_id)
        groups = []
        for group in form.cleaned_data['selected_items']:
            if group != target_group:
                groups.append(group)
        groups.insert(0, target_group)
        return groups

    def form_valid(self, form):
        try:
            AssignmentGroup.merge_groups(self.__get_groups_from_form(form))
        except ValidationError as e:
            messages.warning(
                self.request,
                str(e.message))
        else:
            messages.success(
                self.request,
                "A group with {} has been created!".format(
                    self.__get_merged_candidates_short_name(form.cleaned_data['selected_items'])
                )
            )
        return super(MergeGroupsView, self).form_valid(form)


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  MergeGroupsView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  MergeGroupsView.as_view(),
                  name='filter'),
    ]
