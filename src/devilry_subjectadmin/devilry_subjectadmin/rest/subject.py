from devilry.apps.core.models import Subject
from djangorestframework.resources import ModelResource
from djangorestframework.views import ModelView, InstanceModelView
from djangorestframework.mixins import ListModelMixin
from djangorestframework.permissions import IsAuthenticated

from .auth import IsSubjectAdmin
from .mixins import SelfdocumentingMixin


#class SubjectAdminResource(ModelResource):
    #model = 


class SubjectResource(ModelResource):
    model = Subject
    fields = ('parentnode_id', 'short_name', 'long_name', 'etag')

class ListSubjectRest(SelfdocumentingMixin, ListModelMixin, ModelView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = SubjectResource

    def get_queryset(self):
        return self.resource.model.where_is_admin_or_superadmin(self.user).order_by('short_name')

#class InstanceSubjectRest(InstanceModelView):
    #permissions = (IsAuthenticated, IsSubjectAdmin)
    #resource = SubjectResource
