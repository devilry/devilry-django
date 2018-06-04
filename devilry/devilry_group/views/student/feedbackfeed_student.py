# Python imports
from __future__ import unicode_literals

from django.conf import settings
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit

from devilry.devilry_email.comment_email import comment_email
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group.views.group_comment_edit_base import EditGroupCommentBase
from devilry.utils import setting_utils


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Student view.
    Handles what should be rendered for a student
    on the FeedbackFeed.
    """
    def get_form_heading_text_template_name(self):
        return 'devilry_group/include/student_commentform_headingtext.django.html'

    def get_hard_deadline_info_text(self):
        return setting_utils.get_devilry_hard_deadline_info_text(
            setting_name='DEVILRY_HARD_DEADLINE_INFO_FOR_STUDENTS')

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

    def __send_comment_email(self, comment):
        comment_email.bulk_send_comment_email_to_students_and_examiners(
            domain_url_start=self.request.build_absolute_uri('/'),
            comment_id=comment.id,
            from_student_poster=True)

    def save_object(self, form, commit=False):
        return super(StudentFeedbackFeedView, self).save_object(form, commit=True)

    def perform_after_save(self, comment):
        self.__send_comment_email(comment=comment)


class StudentEditGroupComment(EditGroupCommentBase):
    def dispatch(self, request, *args, **kwargs):
        if not settings.DEVILRY_COMMENT_STUDENTS_CAN_EDIT:
            raise Http404()
        return super(StudentEditGroupComment, self).dispatch(request, *args, **kwargs)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ensure_csrf_cookie(StudentFeedbackFeedView.as_view()),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^groupcomment-edit/(?P<pk>\d+)$',
            ensure_csrf_cookie(StudentEditGroupComment.as_view()),
            name='groupcomment-edit')
    ]
