# django imports
import datetime

from django.utils import timezone
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.db.models import Q

# devilry imports
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models

# crispy forms
from crispy_forms import layout


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
                    obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
                    obj.part_of_grading = False
                    feedbackset.grading_published_datetime = timezone.now()
                    feedbackset.grading_published_by = obj.user
                    obj.published_datetime = timezone.now()
                    feedbackset.full_clean()
                    feedbackset.save()
                    obj = super(ExaminerBaseFeedbackFeedView, self).save_object(form=form, commit=True)
            else:
                self.form_invalid(form)
                obj = super(ExaminerBaseFeedbackFeedView, self).save_object(form=form, commit=False)

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