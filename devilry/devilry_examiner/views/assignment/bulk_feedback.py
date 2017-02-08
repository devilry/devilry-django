from __future__ import unicode_literals

from django import forms
from django.contrib import messages
from django.db import models
from django.db import transaction
from django.db.models.functions import Lower, Concat
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django.views.generic import View
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view

from devilry.apps.core import models as core_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_group import models as group_models


class SelectedAssignmentGroupForm(forms.Form):
    qualification_modelclass = core_models.AssignmentGroup
    invalid_qualification_item_message = 'Invalid assignment group items was selected.'

    #: The items selected as ModelMultipleChoiceField.
    #: If some or all items should be selected by default, override this.
    selected_items = forms.ModelMultipleChoiceField(

        # No items are selectable by default.
        queryset=None,

        # Used if the object to select for some reason does
        # not exist(has been deleted or altered in some way)
        error_messages={
            'invalid_choice': invalid_qualification_item_message,
        }
    )

    #: A wysiwig editor for writing a feedback message.
    feedback_comment_text = forms.CharField(
        widget=AceMarkdownWidget,
        help_text='Add a general comment to the feedback',
        initial=ugettext_lazy('Delivery has been corrected.'))

    def __init__(self, *args, **kwargs):
        selectable_qualification_items_queryset = kwargs.pop('selectable_items_queryset')
        self.assignment = kwargs.pop('assignment')
        super(SelectedAssignmentGroupForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_qualification_items_queryset


class AssignmentGroupTargetRenderer(multiselect2.target_renderer.Target):

    #: The selected item as it is shown when selected.
    #: By default this is :class:`.SelectedQualificationItem`.
    selected_target_renderer = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue

    #: A descriptive name for the items selected.
    descriptive_item_name = 'assignment group'

    def get_submit_button_text(self):
        return 'Submit selected {}(s)'.format(self.descriptive_item_name)

    def get_with_items_title(self):
        return 'Selected {}'.format(self.descriptive_item_name)

    def get_without_items_text(self):
        return 'No {} selected'.format(self.descriptive_item_name)

    def get_field_layout(self):
        return [
            'feedback_comment_text'
        ]


class AssignPointsForm(SelectedAssignmentGroupForm):
    """
    Subclassed the select form and adds a ``Integer`` points field.
    """

    #: Set the amount of points.
    points = forms.IntegerField(
        min_value=0,
        help_text='Add a score that will be given to all selected assignment groups.',
        required=True,
        label=pgettext_lazy('Points'))

    def get_grading_points(self):
        return self.cleaned_data['points']


class PointsTargetRenderer(AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(PointsTargetRenderer, self).get_field_layout()
        layout.append('points')
        return layout


class AssignPassedFailedForm(SelectedAssignmentGroupForm):
    """
    Subclassed the select form and adds a ``Boolean`` field to provide a
    passed/failed grade.
    """

    #: Set delivery as passed or failed.
    passed = forms.BooleanField(
            label=pgettext_lazy('grading', 'Passed?'),
            help_text=pgettext_lazy('grading', 'Check to provide a passing grade.'),
            initial=True,
            required=False)

    def get_grading_points(self):
        if self.cleaned_data['passed']:
            return self.assignment.max_points
        else:
            return 0


class PassedFailedTargetRenderer(AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(PassedFailedTargetRenderer, self).get_field_layout()
        layout.append('passed')
        return layout


class AbstractAssignmentGroupItemListView(multiselect2view.ListbuilderFilterView):
    """
    Abstract class that implements ``ListbuilderFilterView``.

    Adds anonymization and activity filters for the ``AssignmentGroup``s.
    Fetches the ``AssignmentGroups`` through :meth:`~.get_unfiltered_queryset_for_role` and joins
    necessary table used for anonymzation and and annotates for filters.
    """
    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        return super(AbstractAssignmentGroupItemListView, self).dispatch(request, *args, **kwargs)

    def get_default_paginate_by(self, queryset):
        return 5

    def __add_filterlist_items_anonymous_uses_custom_candidate_ids(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymousUsesCustomCandidateIds())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymousUsesCustomCandidateIds())

    def __add_filterlist_items_anonymous(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymous(include_points=False))

    def __add_filterlist_items_not_anonymous(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous(include_points=False))

    def add_filterlist_items(self, filterlist):
        if self.assignment.is_anonymous:
            if self.assignment.uses_custom_candidate_ids:
                self.__add_filterlist_items_anonymous_uses_custom_candidate_ids(filterlist=filterlist)
            else:
                self.__add_filterlist_items_anonymous(filterlist=filterlist)
        else:
            self.__add_filterlist_items_not_anonymous(filterlist=filterlist)
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def __get_candidate_queryset(self):
        return core_models.Candidate.objects\
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

    def __get_examiner_queryset(self):
        return core_models.Examiner.objects\
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

    def get_unfiltered_queryset_for_role(self, role):
        """
        Args:
            role: The CrAdmin role.

        Returns:
            (QuerySet): :obj:`~.devilry.apps.core.model.AssignmentGroup` queryset.
        """
        group_queryset = core_models.AssignmentGroup.objects \
            .filter(parentnode=role) \
            .prefetch_related(
                models.Prefetch('candidates',
                            queryset=self.__get_candidate_queryset())) \
            .prefetch_related(
                models.Prefetch('examiners',
                            queryset=self.__get_examiner_queryset())) \
            .annotate_with_is_waiting_for_feedback() \
            .annotate_with_is_waiting_for_deliveries() \
            .annotate_with_is_corrected() \
            .annotate_with_number_of_private_groupcomments_from_user(user=self.request.user) \
            .annotate_with_number_of_private_imageannotationcomments_from_user(user=self.request.user) \
            .distinct() \
            .select_related('cached_data__last_published_feedbackset',
                            'cached_data__last_feedbackset',
                            'cached_data__first_feedbackset',
                            'parentnode')
        return group_queryset

    def get_value_and_frame_renderer_kwargs(self):
        return {
            'assignment': self.assignment
        }

    def get_form_kwargs(self):
        kwargs = super(AbstractAssignmentGroupItemListView, self).get_form_kwargs()
        kwargs['selectable_items_queryset'] = self.get_unfiltered_queryset_for_role(self.request.cradmin_role)
        kwargs['assignment'] = self.request.cradmin_role
        return kwargs

    def get_selected_groupids(self, posted_form):
        return [item.id for item in posted_form.cleaned_data['selected_items']]

    def get_feedbackset_ids_from_posted_ids(self, form):
        """
        Get list of ids of the last :class:`~.devilry.devilry_group.models.FeedbackSet` from each ``AssignmentGroup``
        in ``form``s cleaned data.

        Args:
            form: cleaned form.

        Returns:
            (list): list of ``FeedbackSet`` ids.
        """
        group_ids = self.get_selected_groupids(posted_form=form)
        feedback_set_ids = self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role) \
            .filter(id__in=group_ids) \
            .values_list('cached_data__last_feedbackset_id', flat=True)
        return list(feedback_set_ids)

    def get_group_anonymous_displaynames(self, form):
        """
        Build a list of anonymized displaynames for the groups that where corrected.

        Args:
            form: posted form

        Returns:
            (list): list of anonymized displaynames for the groups
        """
        groups = form.cleaned_data['selected_items']
        anonymous_display_names = [unicode(group.get_anonymous_displayname(assignment=self.request.cradmin_role))
                                   for group in groups]
        return anonymous_display_names

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def get_filterlist_url(self, filters_string):
        raise NotImplementedError()

    def form_valid(self, form):
        return super(AbstractAssignmentGroupItemListView, self).form_valid(form)

    def add_success_message(self, anonymous_display_names):
        """
        Add list of anonymized displaynames of the groups that received feedback.

        Args:
            anonymous_display_names (list): List of anonymized displaynames for groups.
        """
        raise NotImplementedError()


class AbstractBulkFeedbackListView(AbstractAssignmentGroupItemListView):
    """
    Base class that handles all the logic of bulk creating feedbacks.

    Extend this class with a subclass that uses a form suited for the
    :attr:``~.devilry.apps.core.models.Assignment.grading_system_plugin_id``.

    Example:

        Bulk feedback class points based Assignment::

            class BulkFeedbackPassedFailedView(AbstractBulkFeedbackListView):
                def get_filterlist_url(self, filters_string):
                    return self.request.cradmin_app.reverse_appurl(
                        'bulk-feedback-passedfailed-filter', kwargs={'filters_string': filters_string})

                def get_target_renderer_class(self):
                    return PassedFailedTargetRenderer

                def get_form_class(self):
                    return AssignPassedFailedForm
    """
    model = core_models.AssignmentGroup
    value_renderer_class = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue
    template_name = 'devilry_examiner/assignment/bulk_create_feedback.django.html'

    def get_pagetitle(self):
        return ugettext_lazy('Bulk create feedback')

    def get_filterlist_url(self, filters_string):
        raise NotImplementedError()
    
    def get_unfiltered_queryset_for_role(self, role):
        queryset = super(AbstractBulkFeedbackListView, self).get_unfiltered_queryset_for_role(role)
        return queryset\
            .filter_examiner_has_access(user=self.request.user) \
            .exclude(cached_data__last_published_feedbackset=models.F('cached_data__last_feedbackset'))
    
    def __create_grading_groupcomment(self, feedback_set_id, published_time, text):
        """
        Create an entry of :class:`~.devilry.devilry_group.models.GroupComment` as part of grading
        for the :class:`~.devilry.devilry_group.models.FeedbackSet` that received feedback.

        Args:
            feedback_set_id: comment for this feedback.
            published_time: Time the comment was published.
            text: Text provided by examiner.
        """
        group_models.GroupComment.objects.create(
            feedback_set_id=feedback_set_id,
            part_of_grading=True,
            visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            user=self.request.user,
            user_role=comment_models.Comment.USER_ROLE_EXAMINER,
            text=text,
            comment_type=comment_models.Comment.COMMENT_TYPE_GROUPCOMMENT,
            published_datetime=published_time
        )

    def form_valid(self, form):
        """
        Creates entries of :class:`~.devilry.devilry_group.models.GroupComment`s for all the
        :class:`~.devilry.devilry_group.models.FeedbackSet`s that is given a bulk feedback.

        Note:
            Using ``transaction.atomic()`` for single transaction when creating ``GroupComment``s and
            updating the ``FeedbackSet``s.
            If anything goes wrong, the transaction is rolled back and nothing is saved to the database.

        Args:
            form: cleaned form.
        """
        feedback_set_ids = self.get_feedbackset_ids_from_posted_ids(form=form)
        points = form.get_grading_points()
        text = form.cleaned_data['feedback_comment_text']

        # Cache anonymous display names before transaction. Needed for django messages.
        anonymous_displaynames = self.get_group_anonymous_displaynames(form=form)

        now_without_microseconds = timezone.now().replace(microsecond=0)
        with transaction.atomic():
            for feedback_set_id in feedback_set_ids:
                self.__create_grading_groupcomment(
                    feedback_set_id=feedback_set_id,
                    published_time=now_without_microseconds,
                    text=text)
            group_models.FeedbackSet.objects\
                .filter(id__in=feedback_set_ids)\
                .update(
                    grading_published_by=self.request.user,
                    grading_published_datetime=now_without_microseconds + timezone.timedelta(microseconds=1),
                    grading_points=points)

        self.add_success_message(anonymous_displaynames)
        return super(AbstractAssignmentGroupItemListView, self).form_valid(form=form)

    def add_success_message(self, anonymous_display_names):
        message = ugettext_lazy('Bulk added feedback for %(group_names)s') % {
            'group_names': ', '.join(anonymous_display_names)}
        messages.success(self.request, message=message)


class BulkFeedbackPointsView(AbstractBulkFeedbackListView):
    """
    Handles bulkfeedback for assignment with points-based grading system.
    """
    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'bulk-feedback-points-filter', kwargs={'filters_string', filters_string})

    def get_target_renderer_class(self):
        return PointsTargetRenderer

    def get_form_class(self):
        return AssignPointsForm


class BulkFeedbackPassedFailedView(AbstractBulkFeedbackListView):
    """
    Handles bulkfeedback for assignment with passed/failed grading system.
    """
    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'bulk-feedback-passedfailed-filter', kwargs={'filters_string': filters_string})

    def get_target_renderer_class(self):
        return PassedFailedTargetRenderer

    def get_form_class(self):
        return AssignPassedFailedForm


class BulkFeedbackRedirectView(View):
    """
    Redirects to the appropriate view based on the assignments grading system type.
    """
    def dispatch(self, request, *args, **kwargs):
        grading_plugin_id = self.request.cradmin_role.grading_system_plugin_id
        if grading_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return HttpResponseRedirect(request.cradmin_app.reverse_appurl('bulk-feedback-points'))
        grading_plugin_id = self.request.cradmin_role.grading_system_plugin_id
        if grading_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            return HttpResponseRedirect(request.cradmin_app.reverse_appurl('bulk-feedback-passedfailed'))
        return Http404()
