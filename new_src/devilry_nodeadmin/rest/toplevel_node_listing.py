from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Node



class ToplevelNodeListingResource(ModelResource):
    model = Node
    fields = ('id', 'short_name', 'long_name')


class ToplevelNodeListing( ListModelView ):
    """
    All nodes where the user is either admin (directly on the node), or all
    toplevel nodes if the user is a superuser.
    """
    resource = ToplevelNodeListingResource
    permissions = (IsAuthenticated,)

    def get_queryset( self ):
        if self.request.user.is_superuser:
            qry = Node.objects.filter(parentnode__isnull=True)
        else:
            qry = Node.objects.filter(admins=self.request.user)
        qry = qry.order_by('long_name')
        return qry
