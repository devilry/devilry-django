"""
Manage related users.
"""
from django import forms
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView
from djangorestframework.views import InstanceModelView
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent

from .auth import IsPeriodAdmin
from .mixins import GetParamFormMixin
from .mixins import SelfdocumentingMixin



class ListGetparamForm(forms.Form):
    period = forms.IntegerField(required=True)


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
                    'full_name': user.devilryuserprofile.full_name}

    def period(self, instance):
        if isinstance(instance, self.model):
            return instance.period_id


class ListOrCreateRelatedUserRestMixin(SelfdocumentingMixin):
    getparam_form = ListGetparamForm
    permissions = (IsAuthenticated, IsPeriodAdminPeriodIdKwarg)

    def get_queryset(self):
        period_id = self.kwargs['period_id']
        qry = self.resource.model.objects.filter(period=period_id)
        qry = qry.select_related('user', 'user__devilryuserprofile')
        qry = qry.order_by('user__devilryuserprofile__full_name')
        return qry

    def get(self, request, period_id):
        """
        Get a list of related users. Each entry in the list is a dict/object
        with the following attributes:
        {responsetable}
        """
        return super(ListOrCreateRelatedUserRestMixin, self).get(request)

    def post(self, request, period_id):
        """
        Create a {modelname}.

        # Parameters
        {parameterstable}

        # Returns
        {responsetable}
        """
        return super(ListOrCreateRelatedUserRestMixin, self).post(request)

    def postprocess_docs(self, docs):
        responsetable = self.htmlformat_response_from_fields()
        parameterstable = self.htmlformat_parameters_from_form()
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
        return super(InstanceRelatedUserRestBaseView, self).put(request, id)

    def delete(self, request, period_id, id):
        """
        Delete the {modelname}.

        # Response
        Status 204, with empty body on success.
        """
        return super(InstanceRelatedUserRestBaseView, self).delete(request, id)

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


class ListOrCreateRelatedExaminerRest(ListOrCreateRelatedUserRestMixin,
                                      ListOrCreateModelView,
                                      GetParamFormMixin):
    resource = RelatedExaminerResource


class InstanceRelatedExaminerRest(InstanceRelatedUserRestBaseView):
    resource = RelatedExaminerResource



#############################
# Student
#############################

class RelatedStudentResource(RelatedUserResource):
    model = RelatedStudent
    fields = RelatedUserResource.fields + ('candidate_id',)

class ListOrCreateRelatedStudentRest(ListOrCreateRelatedUserRestMixin,
                                     ListOrCreateModelView,
                                     GetParamFormMixin):
    resource = RelatedStudentResource

class InstanceRelatedStudentRest(InstanceRelatedUserRestBaseView):
    """
    Read, update and delete a single related student.
    """
    resource = RelatedStudentResource
