# Python imports
from __future__ import unicode_literals

# django imports
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# Devilry/cradmin imports
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from django_cradmin import crapp

# 3rd party imports
from django_cradmin.crispylayouts import DefaultSubmit


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Student view.
    Handles what should be rendered for a student
    on the FeedbackFeed.
    """
    def get_devilryrole(self):
        """
        Get the devilryrole for the view.

        Returns:
            str: ``student`` as devilryrole.
        """
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

    def save_object(self, form, commit=False):
        return super(StudentFeedbackFeedView, self).save_object(form, commit=True)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            StudentFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
