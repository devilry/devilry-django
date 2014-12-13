from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry.devilry_qualifiesforexam.registry import qualifiesforexam_plugins


class Plugins(View):
    """
    List all qualifiesforexam plugins.

    # Parameters
    None.

    # Returns
    An array/list with one object/dict for each qualifiesforexam plugin. Each item
    has the following attributes:

    - ``id``: The ID of the plugin.
    - ``title``: The title of the plugin.
    - ``description``: A longer description of the plugin. May contain html markup.
    - ``url``: The URL to the plugin

    """
    permissions = (IsAuthenticated,)

    def get(self, request):
        return qualifiesforexam_plugins.get_configured_list()
