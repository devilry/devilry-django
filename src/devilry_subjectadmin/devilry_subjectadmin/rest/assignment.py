from devilry.apps.core.models import Assignment
from djangorestframework.permissions import IsAuthenticated

from .auth import IsAssignmentAdmin
from .viewbase import BaseNodeInstanceModelView
from .viewbase import BaseNodeListOrCreateView
from .resources import BaseNodeInstanceResource
from devilry.utils.restformat import format_datetime



class AssignmentResourceMixin(object):
    def publishing_time(self, instance):
        if isinstance(instance, self.model):
            return format_datetime(instance.publishing_time)

    def first_deadline(self, instance):
        if isinstance(instance, self.model) and instance.first_deadline:
            return format_datetime(instance.first_deadline)


class AssignmentResource(AssignmentResourceMixin, BaseNodeInstanceResource):
    model = Assignment
    fields = ('id', 'parentnode', 'short_name', 'long_name', 'etag',
              'publishing_time', 'delivery_types', 'scale_points_percent',
              'first_deadline', 'anonymous', 'deadline_handling')

class AssignmentInstanceResource(AssignmentResourceMixin, BaseNodeInstanceResource):
    model = Assignment
    fields = AssignmentResource.fields + ('can_delete', 'admins', 'inherited_admins',
                                          'breadcrumb')


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
