from logging import getLogger
from devilry.apps.core.models import Subject
from djangorestframework.views import ModelView, InstanceModelView
from djangorestframework.mixins import ListModelMixin
from djangorestframework.permissions import IsAuthenticated

from .auth import IsSubjectAdmin
from .mixins import SelfdocumentingMixin
from .mixins import BaseNodeInstanceRestMixin
from .resources import BaseNodeInstanceResource


logger = getLogger(__name__)

class SubjectResource(BaseNodeInstanceResource):
    model = Subject
    fields = ('id', 'parentnode', 'short_name', 'long_name', 'etag')

class SubjectInstanceResource(BaseNodeInstanceResource):
    model = Subject
    fields = SubjectResource.fields + ('can_delete', 'admins')



class ListSubjectRest(SelfdocumentingMixin, ListModelMixin, ModelView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = SubjectResource

    def get_queryset(self):
        qry = self.resource.model.where_is_admin_or_superadmin(self.user)
        qry = qry.order_by('short_name')
        return qry


class InstanceSubjectRest(SelfdocumentingMixin, BaseNodeInstanceRestMixin, InstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsSubjectAdmin)
    resource = SubjectInstanceResource
