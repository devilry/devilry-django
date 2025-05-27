from cradmin_legacy.crinstance import reverse_cradmin_url
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext
from django.views import View
from django_cradmin import crapp

from devilry.apps.core.models.assignment import Assignment
from devilry.apps.core.models.assignment_group import AssignmentGroup


class RedirectToFeedbackAsAdminOrExaminerView(View):
    def get(self, request, *args, **kwargs):
        assignment_group_id = kwargs["assignment_group_id"]
        group = get_object_or_404(AssignmentGroup, id=assignment_group_id)
        if (
            AssignmentGroup.objects.filter(pk=group.pk)
            .filter_examiner_has_access(
                user=self.request.user,
            )
            .exists()
        ):
            url = reverse_cradmin_url(instanceid="devilry_group_examiner", appname="feedbackfeed", roleid=group.pk)
        elif Assignment.objects.filter(pk=group.parentnode_id).filter_user_is_admin(user=self.request.user).exists():
            url = reverse_cradmin_url(instanceid="devilry_group_admin", appname="feedbackfeed", roleid=group.pk)
        else:
            messages.warning(
                self.request,
                gettext(
                    "You tried to access feedback for a group that you do not have access to. "
                    "You most likely had access as admin or examiner previously, but the permissions "
                    "have been removed, and have therefore been redirected to the frontpage."
                ),
            )
            url = reverse_cradmin_url(
                instanceid="devilry_frontpage", appname="frontpage", roleid=None, viewname=crapp.INDEXVIEW_NAME
            )
        return redirect(url)
