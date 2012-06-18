from logging import getLogger
from devilry.apps.core.models import Subject
from djangorestframework.permissions import IsAuthenticated

from .auth import IsSubjectAdmin
from .viewbase import BaseNodeInstanceModelView
from .viewbase import BaseNodeListOrCreateView
from .resources import BaseNodeInstanceResource


logger = getLogger(__name__)

class SubjectResource(BaseNodeInstanceResource):
    model = Subject
    fields = ('id', 'parentnode', 'short_name', 'long_name', 'etag')

class SubjectInstanceResource(BaseNodeInstanceResource):
    model = Subject
    fields = SubjectResource.fields + ('can_delete', 'admins', 'inherited_admins')


class ListOrCreateSubjectRest(BaseNodeListOrCreateView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = SubjectResource


class InstanceSubjectRest(BaseNodeInstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsSubjectAdmin)
    resource = SubjectInstanceResource
