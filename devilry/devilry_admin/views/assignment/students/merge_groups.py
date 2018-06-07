from __future__ import unicode_literals

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
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

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        self.devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and self.devilryrole != 'departmentadmin':
            raise Http404()
        elif (self.assignment.is_semi_anonymous and self.devilryrole == 'periodadmin'):
            raise Http404()
        return super(MergeGroupsView, self).dispatch(request, *args, **kwargs)

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def get_success_url(self):
        if self.get_filters_string():
            return self.get_filterlist_url(self.get_filters_string())
        else:
            return self.request.cradmin_app.reverse_appindexurl()

    def add_filterlist_items(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.StatusSelectFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerCountFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.CandidateCountFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def get_target_renderer_class(self):
        return MergeGroupsTargetRenderer

    def __get_merged_candidates_short_name(self, group):
        candidates = Candidate.objects.filter(assignment_group=group)\
            .select_related('relatedstudent__user')
        ret = ""
        for candidate in candidates:
            ret += ", {}".format(candidate.relatedstudent.user.shortname)
        return ret[2:]

    def __get_groups_from_form(self, form):
        target_group_id = self.request.POST.getlist('selected_items')[0]
        self.target_group = form.cleaned_data['selected_items'].get(id=target_group_id)
        groups = []
        for group in form.cleaned_data['selected_items']:
            if group != self.target_group:
                groups.append(group)
        groups.insert(0, self.target_group)
        return groups

    def form_valid(self, form):
        try:
            AssignmentGroup.merge_groups(self.__get_groups_from_form(form))
        except ValidationError as e:
            messages.warning(
                self.request,
                ugettext_lazy(str(e.message)))
        else:
            candidates_short_name = self.__get_merged_candidates_short_name(self.target_group)
            messages.success(
                self.request,
                ugettext_lazy("A group with %(what)s has been created!") % {'what': candidates_short_name}
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
