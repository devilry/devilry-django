from logging import getLogger
from devilry.apps.core.models import Subject
from djangorestframework.views import ModelView, InstanceModelView
from djangorestframework.mixins import ListModelMixin
from djangorestframework.permissions import IsAuthenticated

from .auth import IsSubjectAdmin
from .mixins import SelfdocumentingMixin
from .errors import PermissionDeniedError
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


class InstanceSubjectRest(InstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsSubjectAdmin)
    resource = SubjectInstanceResource

    def put(self, request, id=None):
        subject = super(InstanceSubjectRest, self).put(request, id=id)
        logger.info('User=%s updated subject %s (%s)', self.user, id, subject)
        return subject

    def get_queryset(self):
        qry = self.resource.model.where_is_admin_or_superadmin(self.user)
        qry = qry.prefetch_related('admins__devilryuserprofile')
        qry = qry.order_by('short_name')
        return qry

    def can_delete(self):
        return self._get_instance_or_404().can_delete()

    def _get_instance_or_404(self, *args, **kwargs):
        from djangorestframework.response import ErrorResponse
        from djangorestframework import status

        model = self.resource.model
        query_kwargs = self.get_query_kwargs(self.request, *args, **kwargs)
        try:
            return self.get_instance(**query_kwargs)
        except model.DoesNotExist:
            raise ErrorResponse(status.HTTP_404_NOT_FOUND, None, {})

    def delete(self, request, *args, **kwargs):
        instance = self._get_instance_or_404(*args, **kwargs)
        instanceid = instance.id
        instanceident = unicode(instance)
        instancename = instance.__class__.__name__
        if instance.can_delete(self.user):
            instance.delete()
            logger.info('User=%s deleted %s %s', self.user, instanceident, instancename)
            return {'id': instanceid}
        else:
            logger.warn(('User=%s tried to delete %s %s. They where rejected '
                         'because of lacking permissions. Since the user-interface',
                         'should make it impossible to perform this action, huge amounts of'
                         'such attempts by this user may be an attempt at trying '
                         'to delete things that they should not attempt to delete.'),
                        self.user, instanceident, instancename)
            raise PermissionDeniedError()
