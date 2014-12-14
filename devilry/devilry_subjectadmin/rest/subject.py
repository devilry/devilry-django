from devilry.apps.core.models import Subject
from djangorestframework.permissions import IsAuthenticated

from .auth import IsSubjectAdmin
from .auth import nodeadmin_required
from devilry.devilry_subjectadmin.rest.viewbase import BaseNodeInstanceModelView
from devilry.devilry_subjectadmin.rest.viewbase import BaseNodeListOrCreateView
from devilry.devilry_subjectadmin.rest.resources import BaseNodeInstanceResource


class SubjectResource(BaseNodeInstanceResource):
    model = Subject
    fields = ('id', 'parentnode', 'short_name', 'long_name', 'etag')

class SubjectInstanceResource(BaseNodeInstanceResource):
    model = Subject
    fields = SubjectResource.fields + ('can_delete', 'admins', 'inherited_admins',
                                       'breadcrumb')

class ListOrCreateSubjectRest(BaseNodeListOrCreateView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = SubjectResource

    def authenticate_postrequest(self, user, parentnode_id):
        nodeadmin_required(user, parentnode_id)


class InstanceSubjectRest(BaseNodeInstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsSubjectAdmin)
    resource = SubjectInstanceResource
