from django.http import HttpResponse

from devilry.apps.core.models import Node, Subject, DevilryUserProfile, Period, RelatedStudent

from djangorestframework.views import ModelView, ListModelView, InstanceModelView
from djangorestframework.mixins import InstanceMixin, ReadModelMixin
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated



class ToplevelNodeListingResource(ModelResource):
    model = Node
    fields = ('id', 'short_name', 'long_name', 'predecessor', 'etag',
            'subject_count', 'assignment_count', 'period_count', 'subjects',
            'breadcrumbs', 'path', 'childnodes')


class ToplevelNodeListing( ListModelView ):
    """
    All nodes where the user is either admin or superadmin
    """
    
    resource = NodeResource
    permissions = (IsAuthenticated,)

    def get_queryset( self ):
        nodes = Node.where_is_admin_or_superadmin( self.request.user )
        nodes = nodes.exclude( parentnode__in=nodes )
        return nodes
