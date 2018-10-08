# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.http import HttpResponseRedirect
from django.utils.translation import pgettext_lazy

from django_cradmin.viewhelpers import multiselect2view, multiselect2, listbuilder, listbuilderview

from devilry.apps.core.models import Assignment, AssignmentGroup, RelatedStudent


class SelectableAssignmentPreMixin(object):
    """
    A mixin that defines the title and description for the renderer.
    """
    def get_title(self):
        if self.assignment.long_name:
            return self.assignment.long_name
        else:
            return self.assignment.short_name

    def get_description(self):
        return '{}: {}'.format('Max points', self.assignment.max_points)


class SelectedAssignmentItem(SelectableAssignmentPreMixin, multiselect2.selected_item_renderer.SelectedItem):
    """
    The selected assignment renderer.
    """
    valuealias = 'assignment'


class SelectableAssignmentItem(SelectableAssignmentPreMixin, multiselect2.listbuilder_itemvalues.ItemValue):
    """
    The selectable assignment renderer.
    """
    valuealias = 'assignment'
    selected_item_renderer_class = SelectedAssignmentItem


class AssignmentItemTargetRenderer(multiselect2.target_renderer.Target):
    def get_with_items_title(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'Selected assignments')

    def get_without_items_text(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'No assignments selected')

    def get_submit_button_text(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'Use selected assignments')

    def get_field_layout(self):
        return [
            'accumulated_score_minimum'
        ]


class SelectAssignmentsForm(forms.Form):
    selected_items = forms.ModelMultipleChoiceField(
        widget=forms.MultipleHiddenInput,
        queryset=Assignment.objects.none())

    #: Add the accumulated score the student needs to have across
    #: the selected assignments.
    accumulated_score_minimum = forms.IntegerField(
        min_value=0,
        required=False,
        label=pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                            'Points'),
        help_text=pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                                'The minimum score the students need to have accumulated across the '
                                'selected assignments.')
    )

    def __init__(self, *args, **kwargs):
        assignment_queryset = kwargs.pop('assignment_queryset')
        super(SelectAssignmentsForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = assignment_queryset


class SelectAssignmentsView(multiselect2view.ListbuilderView):
    """
    Multi-select view for selecting assignments.
    """
    template_name = 'devilry_admin/assignment/students/create_groups/accumulated-score-select-assignments.django.html'
    value_renderer_class = SelectableAssignmentItem
    model = Assignment
    paginate_by = 15

    def get_target_renderer_class(self):
        return AssignmentItemTargetRenderer

    def get_queryset_for_role(self, role):
        return Assignment.objects\
            .exclude(id=role.id)\
            .filter(parentnode_id=role.parentnode.id)\
            .order_by('-publishing_time')

    def get_form_class(self):
        return SelectAssignmentsForm

    def get_form_kwargs(self):
        kwargs = super(SelectAssignmentsView, self).get_form_kwargs()
        kwargs['assignment_queryset'] = self.get_queryset_for_role(role=self.request.cradmin_role)
        return kwargs

    def __clean_session(self):
        if 'accumulated_score_minimum' in self.request.session:
            self.request.session.pop('accumulated_score_minimum')
        if 'selected_assignment_ids' in self.request.session:
            self.request.session.pop('selected_assignment_ids')

    def form_valid(self, form):
        self.__clean_session()
        self.request.session['accumulated_score_minimum'] = form.cleaned_data['accumulated_score_minimum']
        self.request.session['selected_assignment_ids'] = [
            assignment.id for assignment in form.cleaned_data['selected_items']
        ]
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('accumulated-score-preview'))


class RelatedStudentItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'relatedstudent'

    def get_title(self):
        return self.relatedstudent.user.fullname

    def get_description(self):
        return 'Grading points total: {}'.format(self.relatedstudent.grade_points_total)


class PreviewGroupListView(listbuilderview.View):
    # template_name = 'devilry_admin/dashboard/student_feedbackfeed_wizard/student_feedbackfeed_list_users.django.html'
    model = AssignmentGroup
    value_renderer_class = RelatedStudentItemValue
    paginate_by = 35

    def get_pagetitle(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments', 'Select a student')

    def __get_qualifying_students(self, selected_assignment_ids):
        relatedstudents = RelatedStudent.objects\
            .filter(candidate__assignment_group__parentnode_id__in=selected_assignment_ids)\
            .extra(
                select={
                    'grade_points_total': """
                        SELECT COALESCE(SUM(grading_points), 0)
                        FROM devilry_group_feedbackset
                        INNER JOIN devilry_dbcache_assignmentgroupcacheddata 
                          ON (devilry_group_feedbackset.id = devilry_dbcache_assignmentgroupcacheddata.last_feedbackset_id)
                        INNER JOIN core_assignmentgroup
                          ON (core_assignmentgroup.id = devilry_dbcache_assignmentgroupcacheddata.group_id)
                        INNER JOIN core_assignment
                          ON (core_assignment.id = core_assignmentgroup.parentnode_id)
                        WHERE core_assignment.id IN %s 
                    """
                },
            select_params=selected_assignment_ids
        )
        return relatedstudents

    def get_queryset_for_role(self, role):
        accumulated_score_minimum = self.request.session['accumulated_score_minimum']
        selected_assignment_ids = self.request.session['selected_assignment_ids']
        return self.__get_qualifying_students(selected_assignment_ids=selected_assignment_ids)
        # return AssignmentGroup.objects\
        #     .filter(parentnode_id__in=selected_assignment_ids)\
        #     .filter(cached_data__last_published_feedbackset__isnull=False)
