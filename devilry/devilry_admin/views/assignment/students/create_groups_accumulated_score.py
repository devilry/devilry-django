# -*- coding: utf-8 -*-


from decimal import Decimal

from django import forms
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import pgettext_lazy

from cradmin_legacy.viewhelpers import multiselect2view, multiselect2, listbuilder, listbuilderview

from devilry.apps.core.models import Assignment, AssignmentGroup, RelatedStudent, Candidate


class SelectAssignmentItemValuePreMixin(object):
    """
    A mixin that defines the title and description for the renderer.
    """
    def get_title(self):
        if self.assignment.long_name:
            return self.assignment.long_name
        else:
            return self.assignment.short_name

    @property
    def grading_plugin_label(self):
        if self.assignment.grading_system_plugin_id == Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                                 'Passed/failed')
        if self.assignment.grading_system_plugin_id == Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                                 'Points')
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'Unknown grading plugin.')

    def get_description(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'No information available')


class SelectedAssignmentItem(SelectAssignmentItemValuePreMixin, multiselect2.selected_item_renderer.SelectedItem):
    """
    The selected assignment renderer. Appears on the right side when selected.
    """
    valuealias = 'assignment'
    template_name = 'devilry_admin/assignment/students/create_groups/grading_points_based/selected-assignment-item-value.django.html'


class SelectableAssignmentItem(SelectAssignmentItemValuePreMixin, multiselect2.listbuilder_itemvalues.ItemValue):
    """
    The selectable assignment renderer. Appears on the left side.
    """
    valuealias = 'assignment'
    template_name = 'devilry_admin/assignment/students/create_groups/grading_points_based/selectable-assignment-item-value.django.html'
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
            'points_threshold'
        ]


class SelectAssignmentsForm(forms.Form):
    selected_items = forms.ModelMultipleChoiceField(
        widget=forms.MultipleHiddenInput,
        queryset=Assignment.objects.none())

    #: Add the accumulated score the student needs to have across
    #: the selected assignments.
    points_threshold = forms.IntegerField(
        min_value=0,
        required=True,
        label=pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                            'Points threshold'),
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
    template_name = 'devilry_admin/assignment/students/create_groups/grading_points_based/select-assignments.django.html'
    value_renderer_class = SelectableAssignmentItem
    model = Assignment
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        self.clear_session_data()
        return super(SelectAssignmentsView, self).dispatch(request=request, *args, **kwargs)

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

    def clear_session_data(self):
        """
        Removes `selected_assignment_ids` and `points_threshold` from session data.
        """
        if 'from_select_assignment_view' in self.request.session:
            self.request.session.pop('from_select_assignment_view')
        if 'points_threshold' in self.request.session:
            self.request.session.pop('points_threshold')
        if 'selected_assignment_ids' in self.request.session:
            self.request.session.pop('selected_assignment_ids')

    def form_valid(self, form):
        self.clear_session_data()
        self.request.session['from_select_assignment_view'] = ''
        self.request.session['points_threshold'] = form.cleaned_data['points_threshold']
        self.request.session['selected_assignment_ids'] = [
            assignment.id for assignment in form.cleaned_data['selected_items']
        ]
        return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appurl('accumulated-score-preview')))


class RelatedStudentItemValue(listbuilder.itemvalue.TitleDescription):
    template_name = 'devilry_admin/assignment/students/create_groups/grading_points_based/preview-relatedstudent-item-value.django.html'
    valuealias = 'relatedstudent'

    def get_title(self):
        return '{} ({})'.format(self.relatedstudent.user.fullname, self.relatedstudent.user.shortname)

    def get_description(self):
        return 'Grading points total: {}'.format(self.relatedstudent.grade_points_total)


class PreviewRelatedstudentsListView(listbuilderview.View):
    template_name = 'devilry_admin/assignment/students/create_groups/grading_points_based/preview.django.html'
    model = RelatedStudent
    value_renderer_class = RelatedStudentItemValue
    paginate_by = 35

    def dispatch(self, request, *args, **kwargs):
        if 'from_select_assignment_view' not in request.session or \
           'selected_assignment_ids' not in request.session or \
           'points_threshold' not in request.session:
            raise Http404()
        return super(PreviewRelatedstudentsListView, self).dispatch(request=request, *args, **kwargs)

    def get_pagetitle(self):
        assignment_long_name = self.request.cradmin_role.long_name
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'Students that will be added to %(assignment_long_name)s') % {
            'assignment_long_name': assignment_long_name
        }

    def get_no_items_message(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'No students. This means that either all students that qualify are already '
                             'on the assignment, or the students total grading points are below the configured '
                             'threshold.')

    @property
    def selected_assignment_ids(self):
        """
        Get `selected_assignment_ids` from session data.
        """
        return self.request.session.get('selected_assignment_ids', None)

    @property
    def points_threshold(self):
        """
        Get `points_threshold` from session data.
        """
        return self.request.session.get('points_threshold', None)

    def clear_session_data(self):
        """
        Removes `selected_assignment_ids` and `points_threshold` from session data.
        """
        if 'from_select_assignment_view' in self.request.session:
            self.request.session.pop('from_select_assignment_view')
        if self.selected_assignment_ids:
            self.request.session.pop('selected_assignment_ids')
        if self.points_threshold:
            self.request.session.pop('points_threshold')

    def __get_relatedstudent_ids_already_on_assignment(self):
        """
        Get IDs of students already on the assignment.
        """
        assignment = self.request.cradmin_role
        return RelatedStudent.objects\
            .filter(period=assignment.parentnode,
                    candidate__assignment_group__parentnode=assignment) \
            .values_list('id', flat=True)

    def __get_relatedstudents(self, selected_assignment_ids, points_threshold):
        """
        Perform query to fetch all qualifying related students.

        The following is filtered:
            - Candidate must be in an AssignmentGroup connected to selected assignments.
            - Must be active
            - Excludes RelatedStudents already on the assignment.
            - Filter away all RelatedStudents with a grading point total below the threshold.
        """
        queryset = RelatedStudent.objects \
            .filter(candidate__assignment_group__parentnode_id__in=selected_assignment_ids) \
            .filter(active=True) \
            .distinct()

        # Total number of RelatedStudents on across the selected assignments
        self._cached_relatedstudent_total_count = queryset.count()

        queryset = queryset.exclude(id__in=self.__get_relatedstudent_ids_already_on_assignment())\
            .annotate_with_total_grading_points(assignment_ids=selected_assignment_ids) \
            .filter(grade_points_total__gte=points_threshold) \
            .order_by('-grade_points_total')

        # Number of RelatedStudents that will be added to the assignment
        self._cached_relatedstudent_add_count = queryset.count()
        return queryset

    def __get_selected_assignments_queryset(self):
        return Assignment.objects\
            .filter(id__in=self.selected_assignment_ids)

    def get_queryset_for_role(self, role):
        return self.__get_relatedstudents(
            selected_assignment_ids=self.selected_assignment_ids,
            points_threshold=self.points_threshold)

    def __add_success_message(self):
        """
        Add success message after post.
        """
        message = pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                                '%(num_relatedstudents)s student(s) added to %(assignment_long_name)s') % {
            'num_relatedstudents': self._cached_relatedstudent_add_count,
            'assignment_long_name': self.request.cradmin_role.long_name
        }
        messages.success(request=self.request, message=message)

    def __add_students_to_assignment(self):
        relatedstudent_queryset = self.get_queryset()
        AssignmentGroup.objects.bulk_create_groups(
            created_by_user=self.request.user,
            assignment=self.request.cradmin_role,
            relatedstudents=relatedstudent_queryset
        )

    def post(self, request, *args, **kwargs):
        if 'confirm' in request.POST:
            self.__add_students_to_assignment()
            self.__add_success_message()
            self.clear_session_data()
            return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appindexurl()))
        self.clear_session_data()
        return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appindexurl()))

    def get_context_data(self, **kwargs):
        context = super(PreviewRelatedstudentsListView, self).get_context_data(**kwargs)
        points_threshold = self.points_threshold
        selected_assignments = self.__get_selected_assignments_queryset()
        selected_assignments_max_score = selected_assignments.aggregate(Sum('max_points'))['max_points__sum']
        context['points_threshold'] = points_threshold
        context['selected_assignments_total_max_score'] = selected_assignments_max_score
        context['threshold_percentage'] = ((float(points_threshold)/float(selected_assignments_max_score)) * 100.0)
        context['selected_assignments'] = selected_assignments
        context['relatedstudent_total_count'] = self._cached_relatedstudent_total_count
        context['relatedstudent_add_count'] = self._cached_relatedstudent_add_count
        return context
