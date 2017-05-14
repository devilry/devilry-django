from __future__ import unicode_literals

from django import forms
from django.contrib import messages
from django.db import models
from django.db.models.functions import Lower, Concat
from django.shortcuts import redirect
from django.utils.translation import pgettext_lazy
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import multiselect2view

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Candidate, Examiner, RelatedExaminer, Assignment, AssignmentGroup
from devilry.apps.core.models import RelatedStudent
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class GroupViewMixin(object):
    model = coremodels.AssignmentGroup
    filterview_name = None

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        return super(GroupViewMixin, self).dispatch(request, *args, **kwargs)

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            self.filterview_name,
            kwargs={'filters_string': filters_string})

    def add_filterlist_items(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.StatusSelectFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.IsPassingGradeFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.PointsFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerCountFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.CandidateCountFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def get_unfiltered_queryset_for_role(self, role):
        candidatequeryset = Candidate.objects\
            .select_related('relatedstudent__user')\
            .only(
                'candidate_id',
                'assignment_group',
                'relatedstudent__candidate_id',
                'relatedstudent__automatic_anonymous_id',
                'relatedstudent__user__shortname',
                'relatedstudent__user__fullname',
            )\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))
        examinerqueryset = Examiner.objects\
            .select_related('relatedexaminer__user')\
            .only(
                'relatedexaminer',
                'assignmentgroup',
                'relatedexaminer__automatic_anonymous_id',
                'relatedexaminer__user__shortname',
                'relatedexaminer__user__fullname',
            )\
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))
        queryset = coremodels.AssignmentGroup.objects\
            .filter(parentnode=self.assignment)\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=candidatequeryset))\
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=examinerqueryset))\
            .annotate_with_is_waiting_for_feedback_count()\
            .annotate_with_is_waiting_for_deliveries_count()\
            .annotate_with_is_corrected_count() \
            .annotate_with_number_of_private_groupcomments_from_user(user=self.request.user) \
            .annotate_with_number_of_private_imageannotationcomments_from_user(user=self.request.user)\
            .distinct() \
            .select_related('cached_data__last_published_feedbackset',
                            'cached_data__last_feedbackset',
                            'cached_data__first_feedbackset',
                            'parentnode')
        return queryset

    def get_status_filter_value(self):
        status_value = self.get_filterlist().filtershandler.get_cleaned_value_for('status')
        if not status_value:
            status_value = 'all'
        return status_value

    def __get_unfiltered_queryset_for_role(self):
        return self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role)

    def __get_total_groupcount(self):
        return self.__get_unfiltered_queryset_for_role().count()

    # def __get_filtered_groupcount(self):
    #     return self.get_queryset().count()

    def __get_excluding_filters_is_applied(self, total_groupcount):
        return self.get_filterlist().filter(
            queryobject=self.__get_unfiltered_queryset_for_role()
        ).count() < total_groupcount

    def get_filtered_all_students_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .count()

    def get_filtered_waiting_for_feedback_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .filter(annotated_is_waiting_for_feedback__gt=0)\
            .count()

    def get_filtered_waiting_for_deliveries_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .filter(annotated_is_waiting_for_deliveries__gt=0)\
            .count()

    def get_filtered_corrected_count(self):
        return self.get_filterlist()\
            .filter(queryobject=self.__get_unfiltered_queryset_for_role(),
                    exclude={'status'})\
            .filter(annotated_is_corrected__gt=0)\
            .count()

    def __get_distinct_relatedexaminer_ids(self):
        if not hasattr(self, '_distinct_relatedexaminer_ids'):
            self._distinct_relatedexaminer_ids = Examiner.objects\
                .filter(assignmentgroup__in=self.__get_unfiltered_queryset_for_role())\
                .values_list('relatedexaminer_id', flat=True)\
                .distinct()
            self._distinct_relatedexaminer_ids = list(self._distinct_relatedexaminer_ids)
        return self._distinct_relatedexaminer_ids

    def get_distinct_relatedexaminers(self):
        return RelatedExaminer.objects\
            .filter(id__in=self.__get_distinct_relatedexaminer_ids())\
            .select_related('user')\
            .order_by(Lower(Concat('user__fullname', 'user__shortname')))

    def __get_distinct_relatedstudent_ids(self):
        if not hasattr(self, '_distinct_relatedstudent_ids'):
            self._distinct_relatedstudent_ids = Candidate.objects\
                .filter(assignment_group__in=self.__get_unfiltered_queryset_for_role())\
                .values_list('relatedstudent_id', flat=True)\
                .distinct()
            self._distinct_relatedstudent_ids = list(self._distinct_relatedstudent_ids)
        return self._distinct_relatedstudent_ids

    def get_distinct_relatedstudents(self):
        return RelatedStudent.objects\
            .filter(id__in=self.__get_distinct_relatedstudent_ids())\
            .select_related('user')\
            .order_by(Lower(Concat('user__fullname', 'user__shortname')))

    def get_context_data(self, **kwargs):
        context = super(GroupViewMixin, self).get_context_data(**kwargs)
        context['assignment'] = self.assignment
        context['status_filter_value_normalized'] = self.get_status_filter_value()
        total_groupcount = self.__get_total_groupcount()
        context['excluding_filters_is_applied'] = \
            self.__get_excluding_filters_is_applied(
                total_groupcount=total_groupcount)
        return context


class BaseInfoView(GroupViewMixin, listbuilderview.FilterListMixin, listbuilderview.View):
    template_name = 'devilry_admin/assignment/students/groupview_base/base-info-view.django.html'

    def get_value_renderer_class(self):
        devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if devilryrole == 'departmentadmin':
            return devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue
        elif devilryrole == 'subjectadmin':
            if self.assignment.anonymizationmode == Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
                return devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminItemValue
            else:
                return devilry_listbuilder.assignmentgroup.SubjectAdminItemValue
        elif devilryrole == 'periodadmin':
            return devilry_listbuilder.assignmentgroup.PeriodAdminItemValue
        else:
            raise ValueError('Invalid devilryrole: {}'.format(devilryrole))

    def get_value_and_frame_renderer_kwargs(self):
        return {
            'assignment': self.assignment
        }


class SelectedGroupsForm(forms.Form):
    """
    The form we use for validation and selected items extractions
    when the user submits their selection.

    It is just a plain Django form (can also be a ModelForm). You
    just have to make sure that the name of the form field (``selected_items``)
    matches the value returned by ``get_inputfield_name()`` in the
    ``SelectableProductItemValue`` class.
    """
    invalid_students_selected_message =  pgettext_lazy(
            'admin group multiselect submit',
            'Something went wrong. This may happen if changes was made to the selected '
            'students while you where working on them. Please try again.')

    selected_items = forms.ModelMultipleChoiceField(
        queryset=AssignmentGroup.objects.none(),
        error_messages={
            'invalid_choice': invalid_students_selected_message,
        }
    )

    def __init__(self, *args, **kwargs):
        selectable_groups_queryset = kwargs.pop('selectable_groups_queryset')
        super(SelectedGroupsForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_groups_queryset


class BaseMultiselectView(GroupViewMixin, multiselect2view.ListbuilderFilterView):
    template_name = 'devilry_admin/assignment/students/groupview_base/base-multiselect-view.django.html'

    def get_value_renderer_class(self):
        devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if devilryrole == 'departmentadmin':
            return devilry_listbuilder.assignmentgroup.DepartmentAdminMultiselectItemValue
        elif devilryrole == 'subjectadmin':
            if self.assignment.anonymizationmode == Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
                return devilry_listbuilder.assignmentgroup.FullyAnonymousSubjectAdminMultiselectItemValue
            else:
                return devilry_listbuilder.assignmentgroup.SubjectAdminMultiselectItemValue
        elif devilryrole == 'periodadmin':
            return devilry_listbuilder.assignmentgroup.PeriodAdminMultiselectItemValue
        else:
            raise ValueError('Invalid devilryrole: {}'.format(devilryrole))

    def make_value_and_frame_renderer_kwargs(self, value):
        kwargs = super(BaseMultiselectView, self).make_value_and_frame_renderer_kwargs(value=value)
        kwargs['assignment'] = self.assignment
        return kwargs

    def get_target_renderer_class(self):
        return devilry_listbuilder.assignmentgroup.GroupTargetRenderer

    def get_form_class(self):
        return SelectedGroupsForm

    def get_form_kwargs(self):
        kwargs = super(BaseMultiselectView, self).get_form_kwargs()
        kwargs['selectable_groups_queryset'] = self.get_unfiltered_queryset_for_role(
            role=self.request.cradmin_role)
        return kwargs
