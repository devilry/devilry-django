# django imports
import datetime
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
            Q(feedback_set__published_datetime__isnull=False) | Q(instant_publish=True),
            visible_for_students=True,
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
        object.instant_publish = True
        object.visible_for_students = True

        if commit:
            object.save()
            self._convert_temporary_files_to_comment_files(form, object)

        return object


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            StudentFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]