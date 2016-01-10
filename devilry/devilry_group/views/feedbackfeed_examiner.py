# django imports
import datetime

from django.utils import timezone
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _

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
        )

    def get_context_data(self, **kwargs):
        context = super(ExaminerFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'examiner'
        return context

    def get_buttons(self):
        return [layout.Submit('examiner_add_comment_for_examiners',
                           _('Add comment for examiners'),
                           css_class='btn btn-primary'),
                    layout.Submit('examiner_add_public_comment',
                           _('Add public comment'),
                           css_class='btn btn-primary'),
                    layout.Submit('examiner_add_comment_to_feedback_draft',
                           _('Add to feedback'),
                           css_class='btn btn-primary')
                    ]

    def save_object(self, form, commit=True):
        object = super(ExaminerFeedbackFeedView, self).save_object(form)
        object.user_role = 'examiner'

        if form.data.get('examiner_add_comment_for_examiners'):
            object.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
            object.published_datetime = timezone.now()
        elif form.data.get('examiner_add_public_comment'):
            object.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
            object.published_datetime = timezone.now()
        elif form.data.get('examiner_add_comment_to_feedback_draft'):
            object.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS


        if commit:
            if self._convert_temporary_files_to_comment_files(form, object) or len(object.text) > 0:
                object.save()
            # object.save()
            # self._convert_temporary_files_to_comment_files(form, object)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ExaminerFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]