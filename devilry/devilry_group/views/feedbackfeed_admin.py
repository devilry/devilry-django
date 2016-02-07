# Django imports
from django.utils import http
from django.utils.translation import ugettext_lazy as _

# Devilry/cradmin imports
from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models
from django_cradmin import crapp

# 3rd party imports
from crispy_forms import layout


class AdminFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    TODO: Document
    """
    def _get_comments_for_group(self, group):
        return models.GroupComment.objects.filter(
            feedback_set__group=group
        )

    def get_devilryrole(self):
        return 'subjectadmin'

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

    def set_automatic_attributes(self, obj):
        super(AdminFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'admin'

    def save_object(self, form, commit=False):
        obj = super(AdminFeedbackFeedView, self).save_object(form=form)
        if form.data.get('admin_add_comment_for_examiners'):
            obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
        elif form.data.get('admin_public_add_comment'):
            obj.visibility = models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
        obj = super(AdminFeedbackFeedView, self).save_object(form=form, commit=True)
        return obj

    def dispatch(self, request, *args, **kwargs):
        assignment = self.request.cradmin_role.parentnode
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
