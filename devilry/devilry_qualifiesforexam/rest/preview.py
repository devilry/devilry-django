from django.shortcuts import get_object_or_404

from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import ErrorResponse
from djangorestframework import status as statuscodes
from devilry.devilry_qualifiesforexam.pluginhelpers import create_sessionkey
from devilry.apps.core.models import Period
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment
from devilry.devilry_subjectadmin.rest.auth import IsPeriodAdmin


class Preview(View):
    """
    Generate the data required to provide a preview for the qualified for exam wizard.

    # GET

    ## Parameters
    The following parameters are required:

    - ``periodid``: The ID of the period. Supplied as the last part of the URL-path.
      404 is returned unless the user is admin on this period.
    - ``pluginsessionid``: Forwarded from the first page of the wizard. It is an ID
      used to lookup the output from the plugin, included in the listing in the plugins
      REST API.

    ## Returns
    An object/dict with the following attributes:

    - ``pluginoutput``: The serialized output from the plugin.
    - ``perioddata``: All results for all students on the period.
    """
    permissions = (IsAuthenticated, IsPeriodAdmin)

    def get(self, request, id):
        pluginsessionid = self.request.GET.get('pluginsessionid', None)
        if not pluginsessionid:
            raise ErrorResponse(statuscodes.HTTP_400_BAD_REQUEST,
                {'detail': '``pluginsessionid`` is a required parameter'})
        period = get_object_or_404(Period, pk=id)
        previewdata = self.request.session[create_sessionkey(pluginsessionid)]
        grouper = GroupsGroupedByRelatedStudentAndAssignment(period)
        return {
            'perioddata': grouper.serialize(),
            'pluginoutput': previewdata
        }
