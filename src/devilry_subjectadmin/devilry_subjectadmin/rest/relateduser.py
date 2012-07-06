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


class ListOrCreateRelatedUserRestMixin(object):
    getparam_form = ListGetparamForm
    permissions = (IsAuthenticated, IsPeriodAdminPeriodIdKwarg)

    def get_queryset(self):
        period_id = self.kwargs['period_id']
        qry = self.resource.model.objects.filter(period=period_id)
        qry = qry.select_related('user', 'user__devilryuserprofile')
        qry = qry.order_by('user__devilryuserprofile__full_name')
        return qry

    def get(self, request, period_id):
        return super(ListOrCreateRelatedUserRestMixin, self).get(request)

    def post(self, request, period_id):
        return super(ListOrCreateRelatedUserRestMixin, self).post(request)


class InstanceRelatedUserRestBaseView(InstanceModelView):
    permissions = (IsAuthenticated, IsPeriodAdminPeriodIdKwarg)

    def put(self, request, period_id, id):
        return super(ListOrCreateRelatedUserRestMixin, self).post(request, id)

    def delete(self, request, period_id, id):
        return super(ListOrCreateRelatedUserRestMixin, self).post(request, id)


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
    resource = RelatedStudentResource
