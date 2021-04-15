# -*- coding: utf-8 -*-


from django import http
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.views.decorators.csrf import ensure_csrf_cookie
from cradmin_legacy import crapp, crinstance
from cradmin_legacy.crispylayouts import PrimarySubmit

from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_email.comment_email import comment_email
from devilry.devilry_group.views.group_comment_edit_base import EditGroupCommentBase
from devilry.utils import setting_utils


class AdminBaseFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Base view for admin.
    """
    def dispatch(self, request, *args, **kwargs):
        assignment = self.request.cradmin_role.parentnode
        admin_role = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if admin_role != 'departmentadmin':
            if assignment.anonymizationmode == core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
                raise http.Http404
            if assignment.anonymizationmode == core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS:
                if admin_role != 'subjectadmin':
                    raise http.Http404
        return super(AdminBaseFeedbackFeedView, self).dispatch(request, *args, **kwargs)

    def get_hard_deadline_info_text(self):
        return setting_utils.get_devilry_hard_deadline_info_text(
            setting_name='DEVILRY_HARD_DEADLINE_INFO_FOR_EXAMINERS_AND_ADMINS')

    def get_devilryrole(self):
        return self.request.cradmin_instance.get_devilryrole_for_requestuser()

    def set_automatic_attributes(self, obj):
        super(AdminBaseFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'admin'

    def get_backlink_url(self):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='studentoverview',
            roleid=self.request.cradmin_role.parentnode.id
        )

    def get_context_data(self, **kwargs):
        context = super(AdminBaseFeedbackFeedView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        return context


class AdminPublicDiscussView(AdminBaseFeedbackFeedView):
    """
    Admin view for public discussions.

    Discussing with everyone on the :class:`~.devilry.apps.core.models.AssignmentGroup`.
    """
    template_name = 'devilry_group/feedbackfeed_admin/feedbackfeed_admin_discuss.django.html'

    def get_form_heading_text_template_name(self):
        return 'devilry_group/include/admin_commentform_discuss_public_headingtext.django.html'

    def get_buttons(self):
        buttons = super(AdminPublicDiscussView, self).get_buttons()
        buttons.extend([
            PrimarySubmit(
                'admin_add_public_comment',
                gettext_lazy('Add comment'),
                css_class='btn btn-default')
        ])
        return buttons

    def __send_comment_email(self, comment):
        comment_email.bulk_send_comment_email_to_students_and_examiners(
            comment_id=comment.id,
            domain_url_start=self.request.build_absolute_uri('/'))

    def save_object(self, form, commit=False):
        comment = super(AdminPublicDiscussView, self).save_object(form=form)
        comment.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
        comment.published_datetime = timezone.now()
        return super(AdminPublicDiscussView, self).save_object(form=form, commit=True)

    def perform_after_save(self, comment):
        self.__send_comment_email(comment=comment)

    def get_success_url(self):
        return str(self.request.cradmin_app.reverse_appindexurl())


class AdminWithExaminersDiscussView(AdminBaseFeedbackFeedView):
    """
    Admin view for between admins and examiners.

    Discussing with admins and examiners only on the
    :class:`~.devilry.apps.core.models.AssignmentGroup`.
    """
    template_name = 'devilry_group/feedbackfeed_admin/feedbackfeed_admin_examiner_admin_discuss.django.html'

    def get_form_heading_text_template_name(self):
        return 'devilry_group/include/admin_commentform_discuss_examiner_headingtext.django.html'

    def get_buttons(self):
        buttons = super(AdminWithExaminersDiscussView, self).get_buttons()
        buttons.extend([
            PrimarySubmit(
                'admin_add_comment_for_examiners_and_admins',
                gettext_lazy('Add note'))
        ])
        return buttons

    def __send_email_to_examiners(self, comment):
        comment_email.bulk_send_comment_email_to_examiners(
            comment_id=comment.id,
            domain_url_start=self.request.build_absolute_uri('/'))

    def save_object(self, form, commit=False):
        comment = super(AdminWithExaminersDiscussView, self).save_object(form=form)
        comment.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
        comment.published_datetime = timezone.now()
        return super(AdminWithExaminersDiscussView, self).save_object(form=form, commit=True)

    def perform_after_save(self, comment):
        self.__send_email_to_examiners(comment=comment)

    def get_success_url(self):
        return str(self.request.cradmin_app.reverse_appurl(viewname='admin-examiner-discuss'))


class AdminEditGroupCommentView(EditGroupCommentBase):
    """
    """


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ensure_csrf_cookie(AdminPublicDiscussView.as_view()),
            name=crapp.INDEXVIEW_NAME
        ),
        crapp.Url(
            r'^admin-examiner-discuss$',
            ensure_csrf_cookie(AdminWithExaminersDiscussView.as_view()),
            name='admin-examiner-discuss'
        ),
        crapp.Url(
            r'^groupcomment-edit/(?P<pk>\d+)$',
            ensure_csrf_cookie(AdminEditGroupCommentView.as_view()),
            name='groupcomment-edit')
    ]
