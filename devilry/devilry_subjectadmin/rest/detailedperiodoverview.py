from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from devilry.apps.core.models import Period
from devilry.devilry_subjectadmin.rest.auth import IsPeriodAdmin
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment


class DetailedPeriodOverview(View):
    """
    A REST API for ``devilry.utils.groups_groupedby_relatedstudent_and_assignment.GroupsGroupedByRelatedStudentAndAssignment``. Refer
    to the Devilry documentation for more information.

    # GET
    Returns the result of ``GroupsGroupedByRelatedStudentAndAssignment(period).serialize()``.
    If the user is not period admin or superuser, we respond with 403. We also respond with 403
    if the period does not exist.
    """
    permissions = (IsAuthenticated, IsPeriodAdmin)

    def get(self, request, id=None):
        period = Period.objects.get(id=id) # NOTE: We know the period exists because of IsPeriodAdmin
        grouper = GroupsGroupedByRelatedStudentAndAssignment(period)
        return grouper.serialize()
