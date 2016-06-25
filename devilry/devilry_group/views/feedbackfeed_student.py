# django imports
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

# Devilry/cradmin imports
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models
from django_cradmin import crapp

# 3rd party imports
from crispy_forms import layout
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Student view.
    Handles what should be rendered for a student
    on the FeedbackFeed.
    """
    def get_devilryrole(self):
        return 'student'

    def get_buttons(self):
        buttons = super(StudentFeedbackFeedView, self).get_buttons()
        buttons.extend([
            DefaultSubmit(
                'student_add_comment',
                _('Add comment'),
                css_class='btn btn-success'
            )
        ])
        return buttons

    def set_automatic_attributes(self, obj):
        super(StudentFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'student'
        obj.published_datetime = timezone.now()

    def save_object(self, form, commit=True):
        obj = super(StudentFeedbackFeedView, self).save_object(form)
        self._convert_temporary_files_to_comment_files(form, obj)
        if len(obj.text) > 0:
            obj = super(StudentFeedbackFeedView, self).save_object(form, commit=True)
        return obj


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            StudentFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
