# Django imports
from django import forms
from django.contrib import messages
from django.utils import timezone
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _, ugettext_lazy, pgettext_lazy

# Devilry/cradmin imports
from devilry.apps.core import models as core_models
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models
from devilry.devilry_group.views.cradmin_feedbackfeed_base import GroupCommentForm

# 3rd party imports
from crispy_forms import layout


class ExaminerBaseFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Base view for examiner.
    """
    def _get_comments_for_group(self, group):
        """
        Filters the comments a examiner should have access to.
        A examiner is able to see all comment except comments from other examiners
        with :obj:`devilry.devilry_group.models.AbstractGroupComment.visibility` set to
        :obj:`devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_PRIVATE`.

        :param group:
            The :class:`devilry.apps.core.models.AssignmentGroup` the user belongs to.

        Returns:
            List of :class:`devilry.devilry_group.models.GroupComment` objects.
        """
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
            layout.Submit('examiner_add_comment_to_feedback_draft',
                          _('Add to feedback'),
                          css_class='btn btn-default'),
            layout.Submit('examiner_publish_feedback',
                          _('Publish feedback'),
                          css_class='btn btn-primary')
        ])
        return buttons

    def save_object(self, form, commit=True):
        obj = super(ExaminerFeedbackView, self).save_object(form=form)
        if obj.feedback_set.grading_published_datetime is not None:
            messages.warning(self.request, ugettext_lazy('Feedback is already published!'))
        else:
            if form.data.get('examiner_add_comment_to_feedback_draft'):
                obj.visibility = models.GroupComment.VISIBILITY_PRIVATE
                obj.part_of_grading = True
                obj = super(ExaminerFeedbackView, self).save_object(form=form, commit=True)
            elif form.data.get('examiner_publish_feedback'):
                result, error_msg = obj.feedback_set.publish(
                        published_by=obj.user,
                        grading_points=form.get_grading_points())
                if result is False:
                    messages.warning(self.request, ugettext_lazy(error_msg))
                elif len(obj.text) > 0:
                    obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
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

    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group
        ).exclude_private_comments_from_other_users(
            user=self.request.user
        )

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
