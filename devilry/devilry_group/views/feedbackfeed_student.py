# django imports
import datetime

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crapp
from django.db.models import Q

# devilry imports
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models

# crispy forms
from crispy_forms import layout


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):

    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            Q(feedback_set__grading_published_datetime__isnull=False) | Q(visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE),
            # visible_for_students=True,
            visibility=models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            feedback_set__group=group
        )

    def get_context_data(self, **kwargs):
        context = super(StudentFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'student'
        return context

    def get_buttons(self):
        return [
            layout.Submit(
                'student_add_comment',
                _('Add comment'),
                css_class='btn btn-success')
        ]

    def save_object(self, form, commit=True):
        object = super(StudentFeedbackFeedView, self).save_object(form)
        object.user_role = 'student'
        object.published_datetime = timezone.now()

        if commit:
            if self._convert_temporary_files_to_comment_files(form, object) or len(object.text) > 0:
                object.save()
            # object.save()
            # self._convert_temporary_files_to_comment_files(form, object)

        return object


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            StudentFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]