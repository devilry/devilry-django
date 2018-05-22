from __future__ import unicode_literals

from crispy_forms import layout
from django import forms
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django.views.generic import TemplateView
from django_cradmin import crapp, crinstance
from django_cradmin.crispylayouts import CradminFormHelper, PrimarySubmit

from devilry.apps.core.models import Candidate, Assignment, AssignmentGroup
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_assignmentgroup
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
                             'Remove students that did not pass this assignment')


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
        return super(DeleteGroupsView, self).form_valid(form=form)


class SelectAssignmentGroupForm(forms.Form):
    selected_items = forms.ModelMultipleChoiceField(
        widget=forms.MultipleHiddenInput,
        queryset=AssignmentGroup.objects.none())

    def __init__(self, *args, **kwargs):
        assignmentgroup_queryset = kwargs.pop('assignmentgroup_queryset')
        super(SelectAssignmentGroupForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = assignmentgroup_queryset


class DeleteGroupsViewMixin(object):
    form_invalid_message = pgettext_lazy(
        'admin delete_groups',
        'Oups! Something went wrong. This may happen if someone edited '
        'students on the assignment or the semester while you were making '
        'your selection. Please try again.')

    def dispatch(self, request, *args, **kwargs):
        self.assignment = request.cradmin_role
        self.period = self.assignment.parentnode
        return super(DeleteGroupsViewMixin, self).dispatch(request, *args, **kwargs)

    def get_unfiltered_queryset_for_role(self, role):
        return AssignmentGroup.objects.none()

    def get_form_class(self):
        return SelectAssignmentGroupForm

    def get_form(self):
        form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = {
            'assignmentgroup_queryset': self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role)
        }
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return self.request.cradmin_instance.appindex_url('studentoverview')

    def form_valid(self, form):
        selected_assignment_groups = form.cleaned_data['selected_items']
        selected_assignment_groups.delete()
        return redirect(self.get_success_url())

    def get_error_url(self):
        return self.request.get_full_path()

    def form_invalid(self, form):
        print(form.errors)
        messages.error(self.request, self.form_invalid_message)
        return redirect(self.get_error_url())


class ConfirmView(DeleteGroupsViewMixin,
                  listbuilder_assignmentgroup.VerticalFilterListView):
    value_renderer_class = listbuilder_assignmentgroup.AssignmentGroupItemValueTitleDescription

    def dispatch(self, request, *args, **kwargs):
        try:
            self.from_assignment = Assignment.objects.get(id=kwargs.get('from_assignment_id'))
        except Assignment.DoesNotExist:
            raise Http404()
        return super(ConfirmView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return pgettext_lazy(
            'admin delete_groups',
            'Confirm that you want to remove students(groups) that failed %(from_assignment_name)s') % {
                   'from_assignment_name': self.from_assignment.long_name
               }

    def get_pageheading(self):
        return pgettext_lazy(
            'admin delete_groups',
            'Confirm that you want to remove students(groups) that failed %(from_assignment_name)s') % {
                'from_assignment_name': self.from_assignment.long_name
            }

    def get_period(self):
        return self.assignment.period

    def get_filterlist_template_name(self):
        return 'devilry_admin/assignment/students/delete_groups/confirm.django.html'

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            viewname='confirm_delete',
            kwargs={
                'from_assignment_id': self.from_assignment.id,
                'filters_string': filters_string
            })

    def __failed_group_queryset(self):
        return AssignmentGroup.objects\
            .filter(parentnode=self.from_assignment)\
            .filter(cached_data__last_feedbackset__grading_published_datetime__isnull=False)\
            .filter(cached_data__last_feedbackset__grading_points__lt=self.from_assignment.passing_grade_min_points)

    def get_unfiltered_queryset_for_role(self, role):
        failed_group_queryset = self.__failed_group_queryset()
        relatedstudent_ids = list(failed_group_queryset.values_list('candidates__relatedstudent_id', flat=True))
        return AssignmentGroup.objects\
            .filter(parentnode_id=role.id)\
            .filter(candidates__relatedstudent_id__in=relatedstudent_ids)

    def get_form_kwargs(self):
        kwargs = super(ConfirmView, self).get_form_kwargs()
        if self.request.method == 'GET':
            assignmentgroup_queryset = kwargs['assignmentgroup_queryset']
            kwargs['initial'] = {
                'selected_items': assignmentgroup_queryset.values_list('id', flat=True),
            }
        return kwargs

    def __get_formhelper(self):
        helper = CradminFormHelper()
        helper.form_class = 'django-cradmin-form-wrapper devilry-django-cradmin-form-wrapper-top-bottom-spacing'
        helper.form_id = 'devilry_admin_delete_groups_confirm_form'
        helper.layout = layout.Layout(
            'selected_items',
            PrimarySubmit('delete_students', pgettext_lazy('admin delete_groups', 'Remove students'))
        )
        helper.form_action = self.request.get_full_path()
        return helper

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context['no_groups_found'] = not self.get_unfiltered_queryset_for_role(
            role=self.request.cradmin_role).exists()
        context['formhelper'] = self.__get_formhelper()
        context['form'] = self.get_form()
        return context


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
        crapp.Url(r'^confirm/(?P<from_assignment_id>\d+)/(?P<filters_string>.+)?$',
                  ConfirmView.as_view(),
                  name='confirm_delete'),
    ]
