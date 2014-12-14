"""
Manage related users.
"""
from django.db.models import Q

from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView
from djangorestframework.views import InstanceModelView
from djangorestframework.permissions import IsAuthenticated
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent
from .auth import IsPeriodAdmin
from devilry.devilry_subjectadmin.rest.mixins import SelfdocumentingMixin
from .log import logger


class IsPeriodAdminPeriodIdKwarg(IsPeriodAdmin):
    ID_KWARG = 'period_id'


class RelatedUserResource(ModelResource):
    fields = ('id', 'period', 'user', 'tags')

    def user(self, instance):
        if isinstance(instance, self.model):
            user = instance.user
            return {'email': user.email,
                    'username': user.username,
                    'id': user.id,
                    'full_name': user.devilryuserprofile.full_name,
                    'displayname': user.devilryuserprofile.full_name or user.username
                   }

    def period(self, instance):
        if isinstance(instance, self.model):
            return instance.period_id

    def validate_request(self, data, files=None):
        user = data.get('user')
        if user:
            if isinstance(user, dict) and 'id' in user:
                data['user'] = user['id']
        if 'id' in data:
            del data['id']
        return super(RelatedUserResource, self).validate_request(data, files)


class ListRelatedUsersRestMixin(SelfdocumentingMixin):
    def get_period_id(self): # Overridden in ListRelatedUsersOnAssignmentMixin
        return self.kwargs['period_id']

    def get_queryset(self):
        period_id = self.get_period_id()
        qry = self.resource.model.objects.filter(period=period_id)
        qry = qry.select_related('user', 'user__devilryuserprofile')

        querystring = self.request.GET.get('query', '')
        if len(querystring) > 0:
            qry = qry.filter(Q(user__username__icontains=querystring) |
                             Q(user__email__icontains=querystring) |
                             Q(user__devilryuserprofile__full_name__icontains=querystring) |
                             Q(tags__icontains=querystring))

        qry = qry.order_by('user__devilryuserprofile__full_name')
        return qry

    def get(self, request, **kwargs): # NOTE: We take **kwargs because this method is called with period_id or assignment_id(subclass), however it only uses ``request`` (the kwarg is used by permission handlers)
        """
        Without the ``query`` parameter, list all users.

        ## Parameters
        Use the ``query`` parameter in the querystring to search for users by:

        - Full name
        - Username
        - Email
        - Tags

        Uses case-ignore-contains search.

        # Returns
        Get a list of related users. Each entry in the list is a dict/object
        with the following attributes:
        {responsetable}
        """
        return super(ListRelatedUsersRestMixin, self).get(request)

    def postprocess_get_docs(self, docs):
        responsetable = self.htmlformat_response_from_fields()
        return docs.format(modelname=self.resource.model.__name__,
                           responsetable=responsetable)


class CreateRelatedUserRestMixin(SelfdocumentingMixin):

    def post(self, request, period_id):
        """
        Create a {modelname}.

        # Parameters
        {parameterstable}

        # Returns
        {responsetable}
        """
        result = super(CreateRelatedUserRestMixin, self).post(request)
        created = result.cleaned_content
        logger.info('User=%s created %s with id=%s (user_id=%s, tags=%s)', self.user,
                    self.resource.model.__name__, created.id, created.user_id,
                    created.tags)
        return result

    def postprocess_post_docs(self, docs):
        responsetable = self.htmlformat_response_from_fields()
        parameterstable = self.htmlformat_parameters_from_form(override_helptext={'user': 'The ID of the related user.'})
        return docs.format(modelname=self.resource.model.__name__,
                           parameterstable=parameterstable,
                           responsetable=responsetable)


class InstanceRelatedUserRestBaseView(SelfdocumentingMixin, InstanceModelView):
    permissions = (IsAuthenticated, IsPeriodAdminPeriodIdKwarg)

    def put(self, request, period_id, id):
        """
        Update the {modelname}.

        # Parameters
        {parameterstable}

        # Returns
        {responsetable}
        """
        result = super(InstanceRelatedUserRestBaseView, self).put(request, id=id)
        logger.info('User=%s updated %s with id=%s (user_id=%s, tags=%s)', self.user,
                    self.resource.model.__name__, id, result.user_id, result.tags)
        return result

    def delete(self, request, period_id, id):
        """
        Delete the {modelname}.

        # Response
        Status 204, with empty body on success.
        """
        userid = self.get_instance(id=id).user_id
        result = super(InstanceRelatedUserRestBaseView, self).delete(request, id=id)
        logger.info('User=%s deleted %s with id=%s (user_id=%s)', self.user,
                    self.resource.model.__name__, id, userid)
        return result

    def postprocess_docs(self, docs):
        responsetable = self.htmlformat_response_from_fields()
        parameterstable = self.htmlformat_parameters_from_form()
        return docs.format(modelname=self.resource.model.__name__,
                           parameterstable=parameterstable,
                           responsetable=responsetable)


#############################
# Examiner
#############################

class RelatedExaminerResource(RelatedUserResource):
    model = RelatedExaminer


class ListOrCreateRelatedExaminerRest(CreateRelatedUserRestMixin, ListRelatedUsersRestMixin,
                                      ListOrCreateModelView):
    resource = RelatedExaminerResource
    permissions = (IsAuthenticated, IsPeriodAdminPeriodIdKwarg)


class InstanceRelatedExaminerRest(InstanceRelatedUserRestBaseView):
    resource = RelatedExaminerResource



#############################
# Student
#############################

class RelatedStudentResource(RelatedUserResource):
    model = RelatedStudent
    fields = RelatedUserResource.fields + ('candidate_id',)

class ListOrCreateRelatedStudentRest(CreateRelatedUserRestMixin, ListRelatedUsersRestMixin,
                                     ListOrCreateModelView):
    resource = RelatedStudentResource
    permissions = (IsAuthenticated, IsPeriodAdminPeriodIdKwarg)


class InstanceRelatedStudentRest(InstanceRelatedUserRestBaseView):
    """
    Read, update and delete a single related student.
    """
    resource = RelatedStudentResource
