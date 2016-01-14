from crispy_forms import layout
from django.utils import http
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crapp

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models


class AdminFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    TODO: Document
    """
    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group
        )

    def get_context_data(self, **kwargs):
        context = super(AdminFeedbackFeedView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = 'admin'
        return context

    def get_buttons(self):
        return [
            layout.Submit(
                'administrator_add_comment_for_examiners',
                _('Add comment for examiners'),
                css_class='btn btn-primary'),
            layout.Submit(
                'administrator_add_public_comment',
                _('Add comment'),
                css_class='btn btn-primary')
        ]

    def save_object(self, form, commit=False):
        object = super(AdminFeedbackFeedView, self).save_object(form)
        object.user_role = 'admin'

        if form.data.get('admin_add_comment_for_examiners'):
            object.instant_publish = True
            object.visible_for_students = False
        elif form.data.get('admin_public_add_comment'):
            object.instant_publish = True
            object.visible_for_students = True
        # else:
        #     commit=False

        if commit:
            if self._convert_temporary_files_to_comment_files(form, object) or len(object.text):
                object.save()
            # object.save()
            # self._convert_temporary_files_to_comment_files(form, object)

    def dispatch(self, request, *args, **kwargs):
        assignment = self.request.cradmin_role
        if assignment.anonymizationmode == core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            if account_models.PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
                    user=self.request.user, period=assignment.period) != 'departmentadmin':
                raise http.Http404()
        return super(AdminFeedbackFeedView, self).dispatch(request, *args, **kwargs)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AdminFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
