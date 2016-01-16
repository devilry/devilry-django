# django imports
import datetime

from django import forms
from django.contrib import messages
from django.utils import timezone
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _, ugettext_lazy, pgettext_lazy
from django.db.models import Q

# devilry imports
from devilry.apps.core.models import Assignment
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models

# crispy forms
from crispy_forms import layout

from devilry.devilry_group.views.cradmin_feedbackfeed_base import GroupCommentForm


class ExaminerBaseFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    TODO: Document!
    """
    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group
        ).exclude_private_comments_from_other_users(
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super(ExaminerBaseFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'examiner'
        return context

    def get_buttons(self):
        return [
            layout.Submit('examiner_add_comment_for_examiners',
                _('Add comment for examiners'),
               css_class='btn btn-default'),
            layout.Submit('examiner_add_public_comment',
               _('Add public comment'),
               css_class='btn btn-primary'),
            layout.Submit('examiner_add_comment_to_feedback_draft',
                   _('Add to feedback'),
                   css_class='btn btn-default')
        ]

    def set_automatic_attributes(self, obj):
        super(ExaminerBaseFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'examiner'


class AbstractFeedbackForm(GroupCommentForm):

    def get_grading_points(self):
        raise NotImplementedError()


class PassedFailedFeedbackForm(AbstractFeedbackForm):
    passed = forms.BooleanField(
        label=pgettext_lazy('grading', 'Passed?'),
        help_text=pgettext_lazy('grading', 'Check to provide a passing grade.'),
        initial=True,
        required=False)

    @classmethod
    def get_field_layout(self):
        return ['passed']

    def get_grading_points(self):
        if self.cleaned_data['passed']:
            return 1
        else:
            return 0


class PointsFeedbackForm(AbstractFeedbackForm):
    points = forms.IntegerField(
            required=True,
            min_value = 0,
            label=_('Points'))

    def __init__(self, *args, **kwargs):
        super(PointsFeedbackForm, self).__init__(*args, **kwargs)
        self.fields['points'].max_value = self.group.assignment.max_points
        self.fields['points'].help_text = pgettext_lazy('grading', 'Number between 0 and %(max_points)s.') % {
            'max_points': self.group.assignment.max_points
        }

    @classmethod
    def get_field_layout(self):
        return ['points']

    def get_grading_points(self):
        return self.cleaned_data['points']


class ExaminerFeedbackView(ExaminerBaseFeedbackFeedView):
    """
    TODO: Document
    """

    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group
        ).exclude_private_comments_from_other_users(
            user=self.request.user
        )

    def get_form_class(self):
        assignment = self.request.cradmin_role.assignment
        if assignment.grading_system_plugin_id == Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            return PassedFailedFeedbackForm
        elif assignment.grading_system_plugin_id == Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return PointsFeedbackForm
        else:
            raise ValueError('Unsupported grading_system_plugin_id: {}'.format(assignment.grading_system_plugin_id))

    def get_buttons(self):
        return [
            layout.Submit('examiner_add_comment_to_feedback_draft',
                   _('Add to feedback'),
                   css_class='btn btn-default'),
            layout.Submit('examiner_publish_feedback',
                   _('Publish feedback'),
                   css_class='btn btn-primary')
        ]

    def save_object(self, form, commit=True):
        obj = super(ExaminerBaseFeedbackFeedView, self).save_object(form=form, commit=False)

        if form.data.get('examiner_add_comment_to_feedback_draft'):
            obj.visibility = models.GroupComment.VISIBILITY_PRIVATE
            obj.part_of_grading = True
            obj = super(ExaminerBaseFeedbackFeedView, self).save_object(form=form, commit=True)
        elif form.data.get('examiner_publish_feedback'):
            feedbackset = obj.feedback_set
            current_deadline = feedbackset.deadline_datetime
            if feedbackset.deadline_datetime is None:
                current_deadline = feedbackset.group.parentnode.first_deadline
            if current_deadline < timezone.now():
                if feedbackset.grading_points is not None:
                    feedbackset.grading_points = form.get_grading_points()
                    obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
                    obj.part_of_grading = False
                    feedbackset.grading_published_datetime = timezone.now()
                    feedbackset.grading_published_by = obj.user
                    obj.published_datetime = timezone.now()
                    feedbackset.full_clean()
                    feedbackset.save()
                    obj = super(ExaminerBaseFeedbackFeedView, self).save_object(form=form, commit=True)
            else:
                messages.warning(self.request, ugettext_lazy('The deadline has not expired. '
                                                             'Feedback was saved, but not published.'))
        return obj

    def get_form_invalid_message(self, form):
        return 'Cannot publish feedback until deadline has passed!'


class ExaminerDiscussView(ExaminerBaseFeedbackFeedView):
    """
    TODO: Document
    """

    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group,
            part_of_grading=False
        ).exclude_private_comments_from_other_users(
            user=self.request.user
        )

    def get_buttons(self):
        return [
            layout.Submit('examiner_add_comment_for_examiners',
                _('Add comment for examiners'),
               css_class='btn btn-default'),
            layout.Submit('examiner_add_public_comment',
               _('Add public comment'),
               css_class='btn btn-primary'),
        ]

    def save_object(self, form, commit=True):
        obj = super(ExaminerDiscussView, self).save_object(form)

        self._convert_temporary_files_to_comment_files(form, obj)
        if form.data.get('examiner_add_comment_for_examiners'):
            obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
            obj.published_datetime = timezone.now()
        elif form.data.get('examiner_add_public_comment'):
            obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
            obj.published_datetime = timezone.now()

        obj = super(ExaminerDiscussView, self).save_object(form, commit=True)
        return obj

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appurl(viewname='discuss')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^feedback$',
            ExaminerFeedbackView.as_view(),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^discuss$',
            ExaminerDiscussView.as_view(),
            name='discuss'
        )
    ]