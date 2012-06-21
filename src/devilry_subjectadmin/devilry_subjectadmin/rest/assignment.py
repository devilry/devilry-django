from devilry.apps.core.models import Assignment
from djangorestframework.permissions import IsAuthenticated

from .auth import IsAssignmentAdmin
from .viewbase import BaseNodeInstanceModelView
from .viewbase import BaseNodeListOrCreateView
from .resources import BaseNodeInstanceResource


class AssignmentResource(BaseNodeInstanceResource):
    model = Assignment
    fields = ('id', 'parentnode', 'short_name', 'long_name', 'etag',
              'publishing_time', 'delivery_types', 'scale_points_percent',
              'first_deadline')

class AssignmentInstanceResource(BaseNodeInstanceResource):
    model = Assignment
    fields = AssignmentResource.fields + ('can_delete', 'admins', 'inherited_admins')


class ListOrCreateAssignmentRest(BaseNodeListOrCreateView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = AssignmentResource


class InstanceAssignmentRest(BaseNodeInstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = AssignmentInstanceResource
