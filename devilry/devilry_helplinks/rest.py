from devilry.thirdpartylibs.djangorestframework.views import ListModelView
from devilry.thirdpartylibs.djangorestframework.resources import ModelResource
from devilry.thirdpartylibs.djangorestframework.permissions import IsAuthenticated

from .models import HelpLink



class HelpLinkResource(ModelResource):
    model = HelpLink


class ListHelpLinks(ListModelView):
    """
    Provides an API for getting help links.
    """
    resource = HelpLinkResource
    permissions = (IsAuthenticated,)
