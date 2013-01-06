from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry_qualifiesforexam.registry import qualifiesforexam_plugins



class Plugins(View):
    """
    Generate the data required to provide a preview for the qualified for exam wizard.

    # Parameters
    The following parameters are required:

    - ``periodid``: The ID of the period. Supplied as the last part of the URL-path.
    - ``pluginsessionid``: Forwarded from the first page of the wizard. It is an ID
      used to lookup the results from the plugin.

    # Returns
    An object/dict. Each item has the following attributes:

    - ``id``: .

    """
    permissions = (IsAuthenticated,)

    def get(self, request):
        return qualifiesforexam_plugins.get_configured_list()