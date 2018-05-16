from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django.views.generic import TemplateView
from django_cradmin import crapp, crinstance

from devilry.apps.core.models import Candidate
from devilry.devilry_admin.views.assignment.students import groupview_base
from django_cradmin.viewhelpers import listbuilder
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class ChoosePeriodItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'period'
    template_name = 'devilry_admin/assignment/students/delete_groups/choose-period-item-value.django.html'

    def get_extra_css_classes_list(self):
        return ['devilry-django-cradmin-listbuilder-itemvalue-titledescription-lg']

    def get_title(self):
        return pgettext_lazy('admin delete_groups', 'Remove students')

    def get_description(self):
        return pgettext_lazy('admin delete_groups',
                             'You can remove some students on this assignment, or all of them')


class ChooseAssignmentItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'assignment'
    template_name = 'devilry_admin/assignment/students/delete_groups/choose-assignment-item-value.django.html'

    def get_title(self):
        return pgettext_lazy('admin delete_groups',
                             'Select students from %(assignment)s to remove') % {
            'assignment': self.assignment.long_name
        }

    def get_description(self):
        return pgettext_lazy('admin delete_groups',
                             'You can remove all students, or those who did not pass, from this assignment')


class ChooseMethod(TemplateView):
    template_name = 'devilry_admin/assignment/students/delete_groups/choose-method.django.html'

    def get_pagetitle(self):
        assignment = self.request.cradmin_role
        return pgettext_lazy('admin delete_group', 'Remove students from %(assignment)s') % {
            'assignment': assignment.get_path()
        }

    def get_pageheading(self):
        assignment = self.request.cradmin_role
        return pgettext_lazy('admin delete_group', 'Remove students from %(assignment)s') % {
            'assignment': assignment.long_name
        }
        # return pgettext_lazy('admin delete_group', 'Remove students')

    def get_page_subheading(self):
        return pgettext_lazy('admin delete_group',
                             'Please select how you would like to remove students. You will get a '
                             'preview of your choice on the next page before any students are removed.')

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        self.period = self.assignment.parentnode
        return super(ChooseMethod, self).dispatch(request, *args, **kwargs)

    def __make_listbuilder_list(self):
        listbuilder_list = listbuilder.lists.RowList()
        listbuilder_list.append(listbuilder.itemframe.DefaultSpacingItemFrame(
            ChoosePeriodItemValue(value=self.period)))
        assignments = self.period.assignments\
            .order_by('-publishing_time')\
            .exclude(pk=self.assignment.pk)
        for assignment in assignments:
            listbuilder_list.append(
                listbuilder.itemframe.DefaultSpacingItemFrame(
                    ChooseAssignmentItemValue(value=assignment)))
        return listbuilder_list

    def get_context_data(self, **kwargs):
        context = super(ChooseMethod, self).get_context_data(**kwargs)
        context['listbuilder_list'] = self.__make_listbuilder_list()
        context['pagetitle'] = self.get_pagetitle()
        context['pageheading'] = self.get_pageheading()
        context['page_subheading'] = self.get_page_subheading()
        return context


class DeleteGroupsTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Remove students')

    def get_with_items_title(self):
        return ugettext_lazy('Remove the following students:')


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

    def get_success_url(self):
        return self.request.cradmin_instance.appindex_url(appname='delete_groups')
    
    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        candidatecount = self.__count_candidates_in_assignmentgroups(
            groupqueryset=groupqueryset)
        groupqueryset.delete()
        messages.success(self.request, self.get_success_message(candidatecount=candidatecount))
        # return redirect(self.request.get_full_path())
        return super(DeleteGroupsView, self).form_valid(form=form)

class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  ChooseMethod.as_view(),
                  name=crapp.INDEXVIEW_NAME
        ),
        crapp.Url(r'^manual-select$',
                  DeleteGroupsView.as_view(),
                  name='manual_select'),
        crapp.Url(r'^manual-select/filter/(?P<filters_string>.+)?$',
                  DeleteGroupsView.as_view(),
                  name='filter'),
    ]
