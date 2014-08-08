from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from .models import HelpLink



class HelpLinkResource(ModelResource):
    model = HelpLink


class ListHelpLinks(ListModelView):
    """
    Provides an API for getting help links.
    """
    resource = HelpLinkResource
    permissions = (IsAuthenticated,)
