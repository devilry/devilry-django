# django imports
import datetime

from django.utils import timezone
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

# devilry imports
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models

# crispy forms
from crispy_forms import layout


class ExaminerFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
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
        context = super(ExaminerFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'examiner'
        return context

    def get_buttons(self):
        return [
            layout.Submit('examiner_add_comment_for_examiners',
                _('Add comment for examiners'),
               css_class='btn btn-primary'),
            layout.Submit('examiner_add_public_comment',
               _('Add public comment'),
               css_class='btn btn-primary'),
            layout.Submit('examiner_add_comment_to_feedback_draft',
                   _('Add to feedback'),
                   css_class='btn btn-primary')
        ]

    def set_automatic_attributes(self, obj):
        super(ExaminerFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'examiner'

    def save_object(self, form, commit=True):
        obj = super(ExaminerFeedbackFeedView, self).save_object(form)

        self._convert_temporary_files_to_comment_files(form, obj)
        if form.data.get('examiner_add_comment_for_examiners'):
            obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
            obj.published_datetime = timezone.now()
        elif form.data.get('examiner_add_public_comment'):
            obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
            obj.published_datetime = timezone.now()
        elif form.data.get('examiner_add_comment_to_feedback_draft'):
            obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
            obj.part_of_grading = True

        obj = super(ExaminerFeedbackFeedView, self).save_object(form)
        return obj


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ExaminerFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]