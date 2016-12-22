# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django import http
from django.utils.translation import ugettext_lazy as _

# Devilry/cradmin imports
from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit


class AdminFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Admin view.
    Handles what should be rendered for an admin in the feedbackfeed.

    Special case when assignment is fully anonymized. See :func:`dispatch`.
    """
    def get_devilryrole(self):
        """
        See :meth:`~devilry.devilry_group.cradmin_instances.AdminCrInstance.get_devilryrole_for_requestuser`
        """
        return self.request.cradmin_instance.get_devilryrole_for_requestuser()

    def get_context_data(self, **kwargs):
        context = super(AdminFeedbackFeedView, self).get_context_data(**kwargs)
        return context

    def get_buttons(self):
        buttons = super(AdminFeedbackFeedView, self).get_buttons()
        buttons.extend([
            PrimarySubmit(
                'admin_add_comment_for_examiners',
                _('Add comment for examiners'),
                css_class='btn btn-primary'),
            DefaultSubmit(
                'admin_add_public_comment',
                _('Add comment'),
                css_class='btn btn-primary')
        ])
        return buttons

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
        """
        When :obj:`devilry.apps.core.Assignment.anonymizationmode` is set to ``ANONYMIZATIONMODE_FULLY_ANONYMOUS``
        a 404 should be raised if the request user is not a ``departmentadmin``.

        Args:
             request: The request to check.

        Returns:
            HttpResponse: Response returned from dispatch.

        Raises:
             Http404: Is raised if :obj:`~devilry.apps.core.models.Assignment.anonymizationmode` is set to
             ``ANONYMIZATIONMODE_FULLY_ANONYMOUS``, and the requestuser is not a ``departmentadmin``.
        """
        assignment = self.request.cradmin_role.parentnode
        admin_role = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if admin_role == 'departmentadmin':
            return super(AdminFeedbackFeedView, self).dispatch(request, *args, **kwargs)
        if assignment.anonymizationmode == core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise http.Http404
        if assignment.anonymizationmode == core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS:
            if admin_role != 'subjectadmin':
                raise http.Http404
        return super(AdminFeedbackFeedView, self).dispatch(request, *args, **kwargs)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AdminFeedbackFeedView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
