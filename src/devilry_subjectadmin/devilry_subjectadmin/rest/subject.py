from logging import getLogger
from devilry.apps.core.models import Subject
from djangorestframework.resources import ModelResource
from djangorestframework.views import ModelView, InstanceModelView
from djangorestframework.mixins import ListModelMixin
from djangorestframework.permissions import IsAuthenticated

from .auth import IsSubjectAdmin
from .mixins import SelfdocumentingMixin
from .errors import PermissionDeniedError


#class SubjectAdminResource(ModelResource):
    #model = 

logger = getLogger(__name__)

class SubjectResource(ModelResource):
    model = Subject
    fields = ('id', 'parentnode_id', 'short_name', 'long_name', 'etag')

class ListSubjectRest(SelfdocumentingMixin, ListModelMixin, ModelView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = SubjectResource

    def get_queryset(self):
        return self.resource.model.where_is_admin_or_superadmin(self.user).order_by('short_name')


class SubjectInstanceResource(SubjectResource):
    fields = SubjectResource.fields + ('can_delete', 'admins')

    def can_delete(self, instance):
        if not isinstance(instance, Subject):
            return None # This happens if we do not return the instance from one of the functions (I.E.: return a dict instead)
        return instance.can_delete(self.view.user)

    def admins(self, instance):
        if not isinstance(instance, Subject):
            return None # This happens if we do not return the instance from one of the functions (I.E.: return a dict instead)
        admins = {}
        for user in instance.admins.all():
            admins[user.username] = {'email': user.email,
                                     'username': user.username,
                                     'id': user.id,
                                     'full_name': user.devilryuserprofile.full_name}
        return admins

class InstanceSubjectRest(InstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsSubjectAdmin)
    resource = SubjectInstanceResource

    def can_delete(self):
        return self._get_instance_or_404().can_delete()

    def put(self, request, id=None):
        subject = super(InstanceSubjectRest, self).put(request, id=id)
        logger.info('User=%s updated subject %s (%s)', self.user, id, subject)
        return subject

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
