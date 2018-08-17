from __future__ import unicode_literals

import math
import random

from django import forms
from django.contrib import messages
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django.views.generic import TemplateView
from django_cradmin import crapp
from django_cradmin.viewhelpers.mixins import QuerysetForRoleMixin
from devilry.devilry_cradmin import devilry_listfilter
from django_cradmin.viewhelpers import listbuilder, multiselect2, multiselect2view

from devilry.apps.core.models import Candidate
from devilry.apps.core.models import Examiner, RelatedExaminer
from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listfilter import listfilter_relateduser, listfilter_assignmentgroup
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.apps.core.models import period_tag
from devilry.apps.core.models import AssignmentGroup
from django_cradmin.viewhelpers.listbuilder import itemvalue
from django_cradmin.viewhelpers import listbuilderview


class SelectMethodView(TemplateView):
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/select_method.django.html'

    def get_assignment_groups_without_any_examiners(self):
        return AssignmentGroup.objects.filter(parentnode=self.request.cradmin_role, examiners__isnull=True)

    def get_context_data(self, **kwargs):
        context_data = super(SelectMethodView, self).get_context_data(**kwargs)
        assignment = self.request.cradmin_role
        context_data['assignment'] = assignment
        context_data['students_without_examiners_exists'] = self.get_assignment_groups_without_any_examiners().exists()
        return context_data


class TagItemValue(itemvalue.TitleDescription):
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/organize-by-tag-item-value.django.html'

    def __init__(self, assignment_groups, **kwargs):
        super(TagItemValue, self).__init__(**kwargs)
        self.assignment_groups = assignment_groups

    def get_title(self):
        return self.value.displayname


class OrganizeByTagListbuilderView(listbuilderview.View):
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/organize-by-tag.django.html'
    model = period_tag.PeriodTag
    value_renderer_class = TagItemValue
    paginate_by = 10

    def post(self, request, *args, **kwargs):
        self.__organize_examiners()
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())

    def get_pagetitle(self):
        return ugettext_lazy('Organize examiners on tags')

    def __relatedstudent_queryset(self):
        return RelatedStudent.objects\
            .select_related('user', 'period', 'period__parentnode')\
            .order_by('user__shortname')

    def __relatedexaminer_queryset(self):
        return RelatedExaminer.objects\
            .select_related('user', 'period', 'period__parentnode')\
            .order_by('user__shortname')

    def __get_groups_from_candidates(self, candidates, periodtag):
        candidates = candidates.filter(relatedstudent__in=periodtag.relatedstudents.all())\
            .prefetch_related('assignment_group__candidates__relatedstudent__user')
        return [candidate.assignment_group for candidate in candidates]

    def get_listbuilder_list(self, context):
        assignment = self.request.cradmin_role
        listbuilder_list = listbuilder.lists.RowList()
        periodtag_queryset = self.get_queryset_for_role(role=assignment)
        candidate_queryset = Candidate.objects.filter(assignment_group__parentnode=assignment)\
            .select_related(
                'assignment_group',
                'assignment_group__parentnode',
                'assignment_group__parentnode__parentnode',
                'assignment_group__parentnode__parentnode__parentnode',
                'relatedstudent',
                'relatedstudent__user')
        for periodtag in periodtag_queryset:
            listbuilder_list.append(
                listbuilder.itemframe.DefaultSpacingItemFrame(
                    TagItemValue(
                        assignment_groups=self.__get_groups_from_candidates(candidates=candidate_queryset, periodtag=periodtag),
                        value=periodtag,
                    )
                )
            )
        return listbuilder_list

    def get_queryset_for_role(self, role):
        period = role.parentnode
        candidate_queryset = Candidate.objects\
            .filter(assignment_group__parentnode=role)\
            .select_related('assignment_group')\
            .values_list('relatedstudent', flat=True)

        period_tag_queryset = period_tag.PeriodTag.objects\
            .filter_editable_tags_on_period(period=period)\
            .select_related('period', 'period__parentnode')\
            .prefetch_related(
                models.Prefetch(
                    'relatedexaminers',
                    queryset=self.__relatedexaminer_queryset()))\
            .prefetch_related(
                models.Prefetch(
                    'relatedstudents',
                    queryset=self.__relatedstudent_queryset()))\
            .annotate_with_relatedexaminers_count()\
            .annotate_with_relatedstudents_count()\
            .filter(
                models.Q(annotated_relatedexaminers_count__gt=0) &
                models.Q(annotated_relatedstudents_count__gt=0))\
            .filter(relatedstudents__in=candidate_queryset)
        return period_tag_queryset

    def get_context_data(self, **kwargs):
        context_data = super(OrganizeByTagListbuilderView, self).get_context_data(**kwargs)
        assignment = self.request.cradmin_role
        context_data['period_tags_count'] = period_tag.PeriodTag.objects\
            .filter_editable_tags_on_period(period=assignment.parentnode).count()
        context_data['available_period_tags_count'] = self.get_queryset_for_role(role=assignment).count()
        context_data['assignment'] = assignment
        return context_data

    def __clear_examiners(self, group_list):
        Examiner.objects.filter(assignmentgroup__in=group_list).delete()

    def __organize_examiners(self):
        assignment = self.request.cradmin_role
        period_tag_queryset = self.get_queryset_for_role(role=assignment)
        candidates = Candidate.objects \
            .filter(assignment_group__parentnode=assignment)\
            .select_related('assignment_group', 'relatedstudent')
        relatedstudent_to_group_map = {}
        groups = [candidate.assignment_group for candidate in candidates]
        self.__clear_examiners(groups)

        for candidate in candidates:
            if candidate.relatedstudent_id not in relatedstudent_to_group_map:
                relatedstudent_to_group_map[candidate.relatedstudent_id] = [candidate.assignment_group]
            else:
                relatedstudent_to_group_map[candidate.relatedstudent_id].append(candidate.assignment_group)

        examiners_to_create = []
        for periodtag in period_tag_queryset:
            group_list = []
            for relatedstudent in periodtag.relatedstudents.all():
                relatedstudent_id = relatedstudent.id
                if relatedstudent_id in relatedstudent_to_group_map:
                    group_list.extend(relatedstudent_to_group_map[relatedstudent_id])
                    del relatedstudent_to_group_map[relatedstudent_id]

            for relatedexaminer in periodtag.relatedexaminers.all():
                for group in group_list:
                    examiners_to_create.append(Examiner(assignmentgroup=group, relatedexaminer=relatedexaminer))
        Examiner.objects.bulk_create(examiners_to_create)


class RandomOrganizeForm(groupview_base.SelectedGroupsForm):
    selected_relatedexaminers_invalid_choice_message = ugettext_lazy(
            'You must select at least two examiners.')
    selected_relatedexaminers = forms.ModelMultipleChoiceField(
        queryset=RelatedExaminer.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        label=ugettext_lazy('Select at least two examiners:'),
        required=False
    )

    def __make_relatedexaminer_choices(self, relatedexaminerqueryset):
        return [
            (relatedexaminer.id, relatedexaminer.user.get_full_name())
            for relatedexaminer in relatedexaminerqueryset]

    def __init__(self, *args, **kwargs):
        selectable_relatedexaminers_queryset = kwargs.pop('selectable_relatedexaminers_queryset')
        super(RandomOrganizeForm, self).__init__(*args, **kwargs)
        self.fields['selected_relatedexaminers'].queryset = selectable_relatedexaminers_queryset
        self.fields['selected_relatedexaminers'].choices = self.__make_relatedexaminer_choices(
            relatedexaminerqueryset=selectable_relatedexaminers_queryset)

    def clean(self):
        cleaned_data = super(RandomOrganizeForm, self).clean()
        selected_relatedexaminers = cleaned_data.get("selected_relatedexaminers")
        if selected_relatedexaminers.count() < 2:
            self.add_error(
                'selected_relatedexaminers',
                self.selected_relatedexaminers_invalid_choice_message)


class RandomOrganizeTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_with_items_title(self):
        return ugettext_lazy('Select at least two students:')

    def get_submit_button_text(self):
        return ugettext_lazy('Randomly assign selected students to selected examiners')

    def get_field_layout(self):
        return [
            'selected_relatedexaminers'
        ]


class RandomView(groupview_base.BaseMultiselectView):
    filterview_name = 'random'
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/random.django.html'

    def get_target_renderer_class(self):
        return RandomOrganizeTargetRenderer

    def get_form_class(self):
        return RandomOrganizeForm

    def __get_relatedexaminerqueryset(self):
        assignment = self.request.cradmin_role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .exclude(active=False)
        return queryset

    def get_form_kwargs(self):
        kwargs = super(RandomView, self).get_form_kwargs()
        kwargs['selectable_relatedexaminers_queryset'] = self.__get_relatedexaminerqueryset()
        return kwargs

    def get_success_url(self):
        return self.request.cradmin_instance.reverse_url(
            appname='examineroverview',
            viewname=crapp.INDEXVIEW_NAME)

    def __clear_examiners(self, groupqueryset):
        Examiner.objects.filter(assignmentgroup__in=groupqueryset).delete()

    def __random_organize_examiners(self, groupqueryset, relatedexaminerqueryset):
        relatedexaminer_ids = list(relatedexaminerqueryset.values_list('id', flat=True))
        group_ids = list(groupqueryset.values_list('id', flat=True))
        random.shuffle(relatedexaminer_ids)
        random.shuffle(group_ids)
        examiners_to_create = []
        while group_ids:
            for relatedexaminer in relatedexaminer_ids:
                if not group_ids:
                    break
                examiners_to_create.append(
                    Examiner(relatedexaminer_id=relatedexaminer, assignmentgroup_id=group_ids.pop(0))
                )
        Examiner.objects.bulk_create(examiners_to_create)

    def form_invalid_add_global_errormessages(self, form):
        super(RandomView, self).form_invalid_add_global_errormessages(form=form)
        if 'selected_relatedexaminers' in form.errors:
            for errormessage in form.errors['selected_relatedexaminers']:
                messages.error(self.request, errormessage)

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        relatedexaminerqueryset = form.cleaned_data['selected_relatedexaminers']
        self.__clear_examiners(groupqueryset=groupqueryset)
        self.__random_organize_examiners(
            groupqueryset=groupqueryset,
            relatedexaminerqueryset=relatedexaminerqueryset
        )
        messages.success(self.request, ugettext_lazy('Randomly organized students to examiners.'))
        return redirect(self.get_success_url())


class ManualAddOrReplaceExaminersForm(groupview_base.SelectedGroupsForm):
    selected_relatedexaminers_required_message = ugettext_lazy(
            'You must select at least one examiner.')
    selected_relatedexaminers = forms.ModelMultipleChoiceField(
        queryset=RelatedExaminer.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        label=ugettext_lazy('Select examiners:'),
        required=True,
        error_messages={
            'required': selected_relatedexaminers_required_message
        }
    )

    def __make_relatedexaminer_choices(self, relatedexaminerqueryset):
        return [
            (relatedexaminer.id, relatedexaminer.user.get_full_name())
            for relatedexaminer in relatedexaminerqueryset]

    def __init__(self, *args, **kwargs):
        selectable_relatedexaminers_queryset = kwargs.pop('selectable_relatedexaminers_queryset')
        super(ManualAddOrReplaceExaminersForm, self).__init__(*args, **kwargs)
        self.fields['selected_relatedexaminers'].queryset = selectable_relatedexaminers_queryset
        self.fields['selected_relatedexaminers'].choices = self.__make_relatedexaminer_choices(
            relatedexaminerqueryset=selectable_relatedexaminers_queryset)


class ManualAddOrReplaceTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):

    def get_field_layout(self):
        return [
            'selected_relatedexaminers'
        ]


class BaseManualAddOrReplaceView(groupview_base.BaseMultiselectView):
    def get_form_class(self):
        return ManualAddOrReplaceExaminersForm

    def __get_relatedexaminerqueryset(self):
        assignment = self.request.cradmin_role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .exclude(active=False)
        return queryset

    def get_form_kwargs(self):
        kwargs = super(BaseManualAddOrReplaceView, self).get_form_kwargs()
        kwargs['selectable_relatedexaminers_queryset'] = self.__get_relatedexaminerqueryset()
        return kwargs

    def get_success_url(self):
        return self.request.get_full_path()

    def clear_existing_examiners_from_groups(self, groupqueryset):
        raise NotImplementedError()

    def get_ignored_relatedexaminerids_for_group(self, group):
        raise NotImplementedError()

    def __add_examiners(self, groupqueryset, relatedexaminerqueryset):
        examiners = []
        groupcount = 0
        candidatecount = 0
        relatedexaminers = list(relatedexaminerqueryset)
        for group in groupqueryset:
            groupcount += 1
            candidatecount += len(group.candidates.all())
            ignored_relatedexaminers_for_group = self.get_ignored_relatedexaminerids_for_group(group=group)
            for relatedexaminer in relatedexaminers:
                if relatedexaminer.id not in ignored_relatedexaminers_for_group:
                    examiner = Examiner(assignmentgroup=group,
                                        relatedexaminer=relatedexaminer)
                    examiners.append(examiner)
        Examiner.objects.bulk_create(examiners)
        return groupcount, candidatecount, relatedexaminers

    def form_invalid_add_global_errormessages(self, form):
        super(BaseManualAddOrReplaceView, self).form_invalid_add_global_errormessages(form=form)
        if 'selected_relatedexaminers' in form.errors:
            for errormessage in form.errors['selected_relatedexaminers']:
                messages.error(self.request, errormessage)

    def get_success_message_formatting_string(self):
        raise NotImplementedError()

    def get_success_message(self, candidatecount, relatedexaminers):
        examinernames = [relatedexaminer.user.get_full_name()
                         for relatedexaminer in relatedexaminers]
        return self.get_success_message_formatting_string() % {
            'count': candidatecount,
            'examinernames': ', '.join(examinernames)
        }

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        relatedexaminerqueryset = form.cleaned_data['selected_relatedexaminers']
        self.clear_existing_examiners_from_groups(groupqueryset=groupqueryset)
        groupcount, candidatecount, relatedexaminers = self.__add_examiners(
                groupqueryset=groupqueryset,
                relatedexaminerqueryset=relatedexaminerqueryset)
        messages.success(self.request, self.get_success_message(candidatecount=candidatecount,
                                                                relatedexaminers=relatedexaminers))
        return redirect(self.get_success_url())


class ManualAddTargetRenderer(ManualAddOrReplaceTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Add selected examiners to selected students')


class ManualAddView(BaseManualAddOrReplaceView):
    filterview_name = 'manual-add'
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/manual-add.django.html'

    def get_target_renderer_class(self):
        return ManualAddTargetRenderer

    def clear_existing_examiners_from_groups(self, groupqueryset):
        pass  # We do not clear existing examiners in Add view!

    def get_ignored_relatedexaminerids_for_group(self, group):
        # We ignore any examiners currently registered on the group
        return {examiner.relatedexaminer_id for examiner in group.examiners.all()}

    def get_success_message_formatting_string(self):
        return ugettext_lazy('Added %(count)s students to %(examinernames)s.')


class ManualReplaceTargetRenderer(ManualAddOrReplaceTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Replace selected examiners with current examiners for selected students')


class ManualReplaceView(BaseManualAddOrReplaceView):
    filterview_name = 'manual-replace'
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/manual-replace.django.html'

    def get_target_renderer_class(self):
        return ManualReplaceTargetRenderer

    def clear_existing_examiners_from_groups(self, groupqueryset):
        # We clear any existing examiners on for selected groups
        Examiner.objects.filter(assignmentgroup__in=groupqueryset).delete()

    def get_ignored_relatedexaminerids_for_group(self, group):
        # We do not need to ignore any existing examiners - they are removed
        # by :meth:`.clear_existing_examiners_from_groups`
        return []

    def get_success_message_formatting_string(self):
        return ugettext_lazy('Made %(examinernames)s examiner for %(count)s students, replacing any previous '
                             'examiners for those students.')



class SelectedExaminerForm(forms.Form):
    model = Examiner
    invalid_item_message = ugettext_lazy(
        'Something went wrong. This may happen if someone else performed a similar operation '
        'while you where selecting. Refresh the page and try again')

    #: The items selected as ModelMultipleChoiceField.
    #: If some or all items should be selected by default, override this.
    selected_items = forms.ModelMultipleChoiceField(

        # No items are selectable by default.
        queryset=None,

        # Used if the object to select for some reason does
        # not exist(has been deleted or altered in some way)
        error_messages={
            'invalid_choice': invalid_item_message,
        }
    )

    def __init__(self, *args, **kwargs):
        selectable_examiners_queryset = kwargs.pop('selectable_examiners_queryset')
        super(SelectedExaminerForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_examiners_queryset


class ExaminerSelectedItem(multiselect2.selected_item_renderer.SelectedItem):
    valuealias = 'examiner'

    def get_title(self):
        return self.examiner.relatedexaminer.user.get_displayname()


class ExaminerMultiselectItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    valuealias = 'examiner'
    selected_item_renderer_class = ExaminerSelectedItem

    def get_title(self):
        return self.examiner.relatedexaminer.user.get_displayname()


class ExaminerTargetRenderer(multiselect2.target_renderer.Target):

    #: The selected item as it is shown when selected.
    #: By default this is :class:`.SelectedQualificationItem`.
    selected_target_renderer = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue

    #: A descriptive name for the items selected.
    descriptive_item_name = ugettext_lazy('examiners')


class ExaminerMultiSelectListFilterView(multiselect2view.ListbuilderView):
    """
    Abstract class that implements ``ListbuilderFilterView``.

    Adds anonymization and activity filters for the ``AssignmentGroup``s.
    Fetches the ``AssignmentGroups`` through :meth:`~.get_unfiltered_queryset_for_role` and joins
    necessary tables used for anonymzation and annotations used by viewfilters.
    """
    model = Examiner
    value_renderer_class = ExaminerMultiselectItemValue

    def get_pagetitle(self):
        return pgettext_lazy('examiner_bulk_delete_view pagetitle',
                             'Select examiners')

    def get_pageheading(self):
        return pgettext_lazy('examiner_bulk_delete_view pageheading',
                             'Select examiners')

    def get_page_subheading(self):
        return pgettext_lazy('assignment_group_multiselect_list_filter_view page_subheading',
                             'Select the examiners you want to remove.')

    def get_default_paginate_by(self, queryset):
        return 5

    def get_queryset_for_role(self, role):
        return Examiner.objects.filter(assignmentgroup__parentnode=role).distinct('relatedexaminer_id')

    def get_unfiltered_queryset_for_role(self, role):
        return Examiner.objects.filter(assignmentgroup__parentnode=role).distinct('relatedexaminer_id')

    def get_target_renderer_class(self):
        return ExaminerTargetRenderer

    def get_form_class(self):
        return SelectedExaminerForm

    def get_value_and_frame_renderer_kwargs(self):
        return {
            'assignment': self.request.cradmin_role
        }

    def get_form_kwargs(self):
        kwargs = super(ExaminerMultiSelectListFilterView, self).get_form_kwargs()
        kwargs['selectable_examiners_queryset'] = self.get_unfiltered_queryset_for_role(self.request.cradmin_role)
        return kwargs

    def get_selected_groupids(self, posted_form):
        return [item.id for item in posted_form.cleaned_data['selected_items']]

    def form_valid(self, form):
        examiner_queryset = form.cleaned_data['selected_items']
        examiner_queryset.delete()
        return super(ExaminerMultiSelectListFilterView, self).form_valid(form=form)

    def get_success_url(self):
        """
        Defaults to the apps indexview.
        """
        return self.request.cradmin_app.reverse_appindexurl()



class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  SelectMethodView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^random/(?P<filters_string>.+)?$',
                  RandomView.as_view(),
                  name='random'),
        crapp.Url(r'^manual-add/(?P<filters_string>.+)?$',
                  ManualAddView.as_view(),
                  name='manual-add'),
        crapp.Url(r'^manual-replace/(?P<filters_string>.+)?$',
                  ManualReplaceView.as_view(),
                  name='manual-replace'),
        # crapp.Url(r'^manual-remove-examiners$',
        #           ExaminerMultiSelectListFilterView.as_view(),
        #           name='manual-remove-examiners'),
        crapp.Url('^tag$',
                  OrganizeByTagListbuilderView.as_view(),
                  name='organize-by-tag'),
    ]
