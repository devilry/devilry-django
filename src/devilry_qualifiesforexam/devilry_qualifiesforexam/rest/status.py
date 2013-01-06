from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from devilry_qualifiesforexam.pluginhelpers import create_sessionkey
from devilry.apps.core.models import Period
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment
from devilry_subjectadmin.rest.auth import IsPeriodAdmin


class Status(View):
    """
    API for ``QualifiesForFinalExamPeriodStatus``, that lets users list and add statuses.
    Includes marking students as qualified/disqualified for final exams.

    # POST
    Marks students as qualified or unqualfied for final exams. All related students are
    marked on each POST, and the input is simply a list of those that qualifies.

    ## Parameters

    - ``period``: The period ID (last part of the URL-path).
    - ``passing_relatedstudentids``: List of related students that qualifies for final exam.
    - ``status``: The status message.
    - ``plugin``: The plugin that was used to generate the results.
    - ``pluginsettings``: The plugin settings that was used to generate the results.
    """
    permissions = (IsAuthenticated, IsPeriodAdmin)

    def post(self, request, id):
        pluginsessionid = self.request.GET['pluginsessionid']
        period = get_object_or_404(Period, pk=id)
