from devilry.apps.core.models import Period
from djangorestframework.permissions import IsAuthenticated

from .auth import IsPeriodAdmin
from .viewbase import BaseNodeInstanceModelView
from .viewbase import BaseNodeListOrCreateView
from .resources import BaseNodeInstanceResource
from devilry.utils.restformat import format_datetime


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
                                      'breadcrumb')


class ListOrCreatePeriodRest(BaseNodeListOrCreateView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = PeriodResource


class InstancePeriodRest(BaseNodeInstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsPeriodAdmin)
    resource = PeriodInstanceResource
