from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp

from devilry.apps.core.models import Candidate
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class DeleteGroupsTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Delete students')

    def get_with_items_title(self):
        return ugettext_lazy('Delete the following students:')


class DeleteGroupsView(groupview_base.BaseMultiselectView):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/students/delete_groups.django.html'

    def add_filterlist_items(self, filterlist):
        if self.has_delete_with_content_permission():
            super(DeleteGroupsView, self).add_filterlist_items(filterlist=filterlist)
        else:
            filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
            filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())
            filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
            filterlist.append(devilry_listfilter.assignmentgroup.ExaminerCountFilter(view=self))
            filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def get_status_filter_value(self):
        return 'all'

    def get_target_renderer_class(self):
        return DeleteGroupsTargetRenderer

    def has_delete_with_content_permission(self):
        return self.request.cradmin_instance.get_devilryrole_for_requestuser() == 'departmentadmin'

    def get_unfiltered_queryset_for_role(self, role):
        queryset = super(DeleteGroupsView, self).get_unfiltered_queryset_for_role(role=role)
        if self.has_delete_with_content_permission():
            return queryset
        else:
            return queryset\
                .exclude(cached_data__public_student_comment_count__gt=0)\
                .exclude(cached_data__public_examiner_comment_count__gt=0)\
                .exclude(cached_data__last_published_feedbackset__isnull=False)

    def get_context_data(self, **kwargs):
        context = super(DeleteGroupsView, self).get_context_data(**kwargs)
        context['has_delete_with_content_permission'] = self.has_delete_with_content_permission()
        return context

    def get_success_message(self, candidatecount):
        return ugettext_lazy('Removed %(count)s students from this assignment.') % {
            'count': candidatecount
        }

    def __count_candidates_in_assignmentgroups(self, groupqueryset):
        return Candidate.objects\
            .filter(assignment_group__in=groupqueryset)\
            .count()

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        candidatecount = self.__count_candidates_in_assignmentgroups(
            groupqueryset=groupqueryset)
        groupqueryset.delete()
        messages.success(self.request, self.get_success_message(candidatecount=candidatecount))
        return redirect(self.request.get_full_path())


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  DeleteGroupsView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  DeleteGroupsView.as_view(),
                  name='filter'),
    ]
