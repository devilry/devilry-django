from django.core.urlresolvers import reverse
from django.db.models import Count

from djangorestframework.permissions import IsAuthenticated
from .auth import IsPeriodAdmin
from .auth import subjectadmin_required
from devilry.devilry_subjectadmin.rest.viewbase import BaseNodeInstanceModelView
from devilry.devilry_subjectadmin.rest.viewbase import BaseNodeListOrCreateView
from .resources import BaseNodeInstanceResource
from devilry.devilry_rest.serializehelpers import format_datetime
from devilry.apps.core.models import Period


class PeriodResourceMixin(object):
    def start_time(self, instance):
        if isinstance(instance, self.model):
            return format_datetime(instance.start_time)

    def end_time(self, instance):
        if isinstance(instance, self.model):
            return format_datetime(instance.end_time)


class PeriodResource(PeriodResourceMixin, BaseNodeInstanceResource):
    model = Period
    fields = ('id', 'parentnode', 'short_name', 'long_name', 'etag',
              'start_time', 'end_time')


class PeriodInstanceResource(PeriodResourceMixin, BaseNodeInstanceResource):
    model = Period
    fields = PeriodResource.fields + ('can_delete', 'admins', 'inherited_admins',
                                      'breadcrumb',
                                      'number_of_relatedstudents',
                                      'number_of_relatedexaminers')



class PeriodListResource(PeriodResource):
    fields = PeriodResource.fields + ('url',)

    def url(self, instance):
        if isinstance(instance, self.model):
            return reverse('devilry-subjectadmin-rest-period-instance', kwargs={'id': instance.pk})



class ListOrCreatePeriodRest(BaseNodeListOrCreateView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = PeriodListResource

    def authenticate_postrequest(self, user, parentnode_id):
        subjectadmin_required(user, parentnode_id)

    def get_queryset(self):
        qry = super(ListOrCreatePeriodRest, self).get_queryset()
        qry = qry.order_by('-start_time')
        return qry



class InstancePeriodRest(BaseNodeInstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsPeriodAdmin)
    resource = PeriodInstanceResource

    def get_queryset(self):
        qry = super(InstancePeriodRest, self).get_queryset()
        qry = qry.select_related('parentnode', 'parentnode__parentnode')
        qry = qry.prefetch_related('admins', 'admins__devilryuserprofile',
                                   'parentnode__admins', 'parentnode__admins__devilryuserprofile')
        qry = qry.annotate(number_of_relatedstudents=Count('relatedstudent', distinct=True),
                           number_of_relatedexaminers=Count('relatedexaminer', distinct=True))
        return qry
