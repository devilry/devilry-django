# Django imports
from django import forms
from django.contrib import messages
from django.db import models
from django.utils import timezone
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _, ugettext_lazy, pgettext_lazy

# Devilry/cradmin imports
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit

from devilry.apps.core import models as core_models
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.cradmin_feedbackfeed_base import GroupCommentForm

# 3rd party imports
from crispy_forms import layout


class ExaminerBaseFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Base view for examiner.
    """
    def get_devilryrole(self):
        return 'examiner'

    def get_buttons(self):
        return []

    def set_automatic_attributes(self, obj):
        super(ExaminerBaseFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'examiner'


class AbstractFeedbackForm(GroupCommentForm):
    def get_grading_points(self):
        raise NotImplementedError()


class PassedFailedFeedbackForm(AbstractFeedbackForm):
    """
    Form for passed/failed grade plugin.
    """

    #: Set delivery as passed or failed.
    passed = forms.BooleanField(
        label=pgettext_lazy('grading', 'Passed?'),
        help_text=pgettext_lazy('grading', 'Check to provide a passing grade.'),
        initial=True,
        required=False)

    @classmethod
    def get_field_layout(cls):
        return ['passed']

    def get_grading_points(self):
        if self.cleaned_data['passed']:
            return self.group.assignment.max_points
        else:
            return 0


class PointsFeedbackForm(AbstractFeedbackForm):
    """
    Form for point-based grade plugin.
    """

    #: Set points that should be given to the delivery.
    points = forms.IntegerField(
            required=True,
            min_value=0,
            label=_('Points'))

    def __init__(self, *args, **kwargs):
        super(PointsFeedbackForm, self).__init__(*args, **kwargs)
        self.fields['points'].max_value = self.group.assignment.max_points
        self.fields['points'].help_text = pgettext_lazy('grading', 'Number between 0 and %(max_points)s.') % {
            'max_points': self.group.assignment.max_points
        }

    @classmethod
    def get_field_layout(cls):
        return ['points']

    def get_grading_points(self):
        return self.cleaned_data['points']


class ExaminerFeedbackView(ExaminerBaseFeedbackFeedView):
    """
    The examiner feedbackview.
    This is the view where examiner corrects the delivery made by a student
    and is only able to create drafted comments, or publish grading.
    """
    template_name = 'devilry_group/feedbackfeed_examiner_feedback.django.html'

    def get_form_class(self):
        """
        Get the correct form based on what grade plugin that is used.

        Returns:
            A :class:`devilry.devilry_group.views.cradmin_feedbackfeed_base.GroupCommentForm`

        """
        assignment = self.request.cradmin_role.assignment
        if assignment.grading_system_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            return PassedFailedFeedbackForm
        elif assignment.grading_system_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return PointsFeedbackForm
        else:
            raise ValueError('Unsupported grading_system_plugin_id: {}'.format(assignment.grading_system_plugin_id))

    def get_buttons(self):
        buttons = super(ExaminerFeedbackView, self).get_buttons()
        buttons.extend([
            DefaultSubmit('examiner_add_comment_to_feedback_draft',
                          _('Save draft and preview')),
            PrimarySubmit('examiner_publish_feedback',
                          _('Publish feedback'))
        ])
        return buttons

    def save_object(self, form, commit=True):
        obj = super(ExaminerFeedbackView, self).save_object(form=form)
        if obj.feedback_set.grading_published_datetime is not None:
            messages.warning(self.request, ugettext_lazy('Feedback is already published!'))
        else:
            if form.data.get('examiner_add_comment_to_feedback_draft'):
                # If comment is part of a draft, the comment should only be visible to
                # the examiner until draft-publication.
                obj.visibility = group_models.GroupComment.VISIBILITY_PRIVATE
                obj.part_of_grading = True
                obj = super(ExaminerFeedbackView, self).save_object(form=form, commit=True)
            elif form.data.get('examiner_publish_feedback'):
                result, error_msg = obj.feedback_set.publish(
                        published_by=obj.user,
                        grading_points=form.get_grading_points())
                if result is False:
                    messages.warning(self.request, ugettext_lazy(error_msg))
                elif len(obj.text) > 0:
                    # Don't make comment visible to others unless it actaully
                    # contains any text
                    obj.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
                    obj.part_of_grading = True
                    obj.published_datetime = obj.get_published_datetime()
                    obj = super(ExaminerFeedbackView, self).save_object(form=form, commit=True)
        return obj

    def get_form_invalid_message(self, form):
        return 'Cannot publish feedback until deadline has passed!'


class ExaminerDiscussView(ExaminerBaseFeedbackFeedView):
    """
    The examiner discussview.
    This is the view examiner uses for communicating with students and admins in the feedbackfeed.
    """
    template_name = 'devilry_group/feedbackfeed_examiner_discuss.django.html'

    def get_buttons(self):
        buttons = super(ExaminerDiscussView, self).get_buttons()
        buttons.extend([
            layout.Submit('examiner_add_comment_for_examiners',
                          _('Add comment for examiners'),
                          css_class='btn btn-default'),
            layout.Submit('examiner_add_public_comment',
                          _('Add public comment'),
                          css_class='btn btn-primary'),
        ])
        return buttons

    def save_object(self, form, commit=True):
        obj = super(ExaminerDiscussView, self).save_object(form)
        self._convert_temporary_files_to_comment_files(form, obj)
        if form.data.get('examiner_add_comment_for_examiners'):
            obj.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
            obj.published_datetime = timezone.now()
        elif form.data.get('examiner_add_public_comment'):
            obj.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
            obj.published_datetime = timezone.now()

        obj = super(ExaminerDiscussView, self).save_object(form, commit=True)
        return obj

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appurl(viewname='discuss')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ExaminerFeedbackView.as_view(),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^discuss$',
            ExaminerDiscussView.as_view(),
            name='discuss'
        )
    ]
