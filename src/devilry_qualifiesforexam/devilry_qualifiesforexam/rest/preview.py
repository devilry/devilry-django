from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from devilry_qualifiesforexam.pluginhelpers import create_sessionkey
from devilry.apps.core.models import Period
from devilry.utils.groups_groupedby_relatedstudent_and_assignment import GroupsGroupedByRelatedStudentAndAssignment


class Preview(View):
    """
    Generate the data required to provide a preview for the qualified for exam wizard.

    # Parameters
    The following parameters are required:

    - ``periodid``: The ID of the period. Supplied as the last part of the URL-path.
    - ``pluginsessionid``: Forwarded from the first page of the wizard. It is an ID
      used to lookup the output from the plugin.

    # Returns
    An object/dict. Each item has the following attributes:

    - ``id``: .

    """
    permissions = (IsAuthenticated,)

    def get(self, request):
        pluginsessionid = self.request.GET['pluginsessionid']
        periodid = self.request.GET['periodid']
        period = get_object_or_404(Period, pk=periodid)
        previewdata = self.request.session[create_sessionkey(pluginsessionid)]
        grouper = GroupsGroupedByRelatedStudentAndAssignment(period)
        return {
            'perioddata': grouper.serialize(),
            'pluginoutput': previewdata.serialize()
        }
