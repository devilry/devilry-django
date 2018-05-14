from __future__ import unicode_literals

from django import forms
from django.contrib import messages
from django.db import models
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django.views.generic import View

import django_rq

from devilry.apps.core import models as core_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_operations_grouplist
from devilry.devilry_group import models as group_models
from devilry.devilry_email.feedback_email.feedback_email import bulk_send_email


class AssignPointsForm(bulk_operations_grouplist.SelectedAssignmentGroupForm):
    """
    Subclassed the select form and adds a ``IntegerField`` for points.
    """
    #: Set the amount of points.
    points = forms.IntegerField(
        min_value=0,
        help_text='Add a score that will be given to all selected assignment groups.',
        required=True,
        label=pgettext_lazy('Points'))

    def get_grading_points(self):
        return self.cleaned_data['points']


class PointsTargetRenderer(bulk_operations_grouplist.AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(PointsTargetRenderer, self).get_field_layout()
        layout.append('points')
        return layout


class AssignPassedFailedForm(bulk_operations_grouplist.SelectedAssignmentGroupForm):
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


class PassedFailedTargetRenderer(bulk_operations_grouplist.AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(PassedFailedTargetRenderer, self).get_field_layout()
        layout.append('passed')
        return layout


class AbstractBulkFeedbackListView(bulk_operations_grouplist.AbstractAssignmentGroupMultiSelectListFilterView):
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
        displaynames = self.get_group_displaynames(form=form)

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
            bulk_send_email(feedbackset_id_list=feedback_set_ids,
                            domain_url_start=self.request.build_absolute_uri('/'))

        self.add_success_message(displaynames)
        return super(AbstractBulkFeedbackListView, self).form_valid(form=form)

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
            'bulk-feedback-points-filter', kwargs={'filters_string': filters_string})

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
