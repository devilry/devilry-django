"""
Manage related users.
"""
#from devilry.apps.core.models import RelatedStudent, RelatedExaminer
#from devilry.rest.indata import indata
#from devilry.rest.restbase import RestBase

#from auth import periodadmin_required



#class RelatedUserDaoBase(object):
    #"""
    #Base class for RelatedStudentDao and RelatedExaminerDao
    #"""
    #readfields = ['id', 'tags',
                  #'user_id', 'user__username', 'user__email',
                  #'user__devilryuserprofile__full_name']
    #corecls = None

    #def _get_relatedusers(self, periodid):
        #"""
        #Get a list of relateduser dictionaries.
        #"""
        #return self.corecls.objects.filter(period=periodid).select_related('feedback').values(*self.readfields)

    #def list(self, user, periodid):
        #periodadmin_required(user, periodid)
        #return [u for u in self._get_relatedusers(periodid)] # Convert from ValuesQuerySet


#class RelatedStudentDao(RelatedUserDaoBase):
    #"""
    #DAO class for :class:`devilry.apps.core.models.RelatedStudent`.
    #"""
    #readfields = RelatedUserDaoBase.readfields + ['candidate_id']
    #corecls = RelatedStudent

#class RelatedExaminerDao(RelatedUserDaoBase):
    #"""
    #DAO class for :class:`devilry.apps.core.models.RelatedExaminer`
    #"""
    #corecls = RelatedExaminer


#class RestRelatedStudent(RestBase):
    #"""
    #Rest interface for for :class:`devilry.apps.core.models.RelatedStudent`.
    #"""
    #def __init__(self, daocls=RelatedStudentDao, **basekwargs):
        #super(RestRelatedStudent, self).__init__(**basekwargs)
        #self.dao = daocls()

    #@indata(periodid=int)
    #def list(self, periodid):
        #"""
        #Returns a list with one dict for each related student in the given period.
        #Each item in the dict has the following keys:

        #- id --- int
        #- tags --- string (tags are comma separated)
        #- user_id --- int
        #- user__username --- string
        #- user__email --- string
        #- user__devilryuserprofile__full_name --- string
        #- candidate_id --- string
        #"""
        #return self.dao.list(self.user, periodid)


#class RestRelatedExaminer(RestBase):
    #"""
    #Rest interface for for :class:`devilry.apps.core.models.RelatedStudent`.
    #"""
    #def __init__(self, daocls=RelatedExaminerDao, **basekwargs):
        #super(RestRelatedExaminer, self).__init__(**basekwargs)
        #self.dao = daocls()

    #@indata(periodid=int)
    #def list(self, periodid):
        #"""
        #Returns a list with one dict for each related examiner in the given
        #period.  Each item in the dict has the following keys:

        #- id --- int
        #- tags --- string (tags are comma separated)
        #- user_id --- int
        #- user__username --- string
        #- user__email --- string
        #- user__devilryuserprofile__full_name --- string
        #"""
        #return self.dao.list(self.user, periodid)



from django import forms
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView
from djangorestframework.views import InstanceModelView
from djangorestframework.permissions import IsAuthenticated
from devilry.apps.core.models import RelatedExaminer

from .auth import IsPeriodAdmin
from .mixins import GetParamFormMixin



class ListGetparamForm(forms.Form):
    period = forms.IntegerField(required=True)


class IsPeriodAdminGetParam(IsPeriodAdmin):
    def get_id(self):
        return self.view.GETPARAMS['period']


class RelatedExaminerResource(ModelResource):
    model = RelatedExaminer
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


class ListOrCreateRelatedExaminerRest(ListOrCreateModelView, GetParamFormMixin):
    getparam_form = ListGetparamForm
    permissions = (IsAuthenticated, IsPeriodAdminGetParam)
    resource = RelatedExaminerResource

    def get_queryset(self):
        qry = self.resource.model.objects.filter(period=self.GETPARAMS['period'])
        qry = qry.select_related('user', 'user__devilryuserprofile')
        qry = qry.order_by('user__devilryuserprofile__full_name')
        return qry


class InstanceRelatedExaminerRest(InstanceModelView):
    permissions = (IsAuthenticated, IsPeriodAdmin)
    resource = RelatedExaminerResource
