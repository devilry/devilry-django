# Python imports
from __future__ import unicode_literals

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit

from devilry.devilry_group.views import cradmin_feedbackfeed_base


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Student view.
    Handles what should be rendered for a student
    on the FeedbackFeed.
    """
    def get_form_heading_text_template_name(self):
        return 'devilry_group/include/student_commentform_headingtext.django.html'

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
            PrimarySubmit(
                'student_add_comment',
                _('Add delivery or question')
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
            ensure_csrf_cookie(StudentFeedbackFeedView.as_view()),
            name=crapp.INDEXVIEW_NAME),
    ]
