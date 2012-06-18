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

    def get_restdocs(self):
        return """
        List the subjects where the authenticated user is admin.

        ## Returns
        Map/dict with the following attributes:

        """


class InstanceSubjectRest(SelfdocumentingMixin, BaseNodeInstanceRestMixin, InstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsSubjectAdmin)
    resource = SubjectInstanceResource

    def postprocess_docs(self, docs):
        return docs.format(parametertable=self.htmlformat_parameters_from_form(),
                           fieldstable=self.htmlformat_response_from_fields())

    def get_restdocs(self):
        return """
        Get info about the subject and its admins.

        ## Returns
        Map/dict with the following attributes:

        {fieldstable}
        """

    def put_restdocs(self):
        return """
        Update the subject and its admins.

        ## Parameters
        {parametertable}
        """
