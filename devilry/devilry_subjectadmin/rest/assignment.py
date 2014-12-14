from datetime import datetime

from django.db.models import Count

from djangorestframework.permissions import IsAuthenticated
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Examiner
from devilry.devilry_rest.serializehelpers import format_datetime
from devilry.devilry_rest.serializehelpers import format_timedelta
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginNotInRegistryError
from .auth import IsAssignmentAdmin
from .auth import periodadmin_required
from devilry.devilry_subjectadmin.rest.viewbase import BaseNodeInstanceModelView
from devilry.devilry_subjectadmin.rest.viewbase import BaseNodeListOrCreateView
from .resources import BaseNodeInstanceResource


class AssignmentResourceMixin(object):
    def publishing_time(self, instance):
        if isinstance(instance, self.model):
            return format_datetime(instance.publishing_time)

    def publishing_time_offset_from_now(self, instance):
        if isinstance(instance, self.model):
            return format_timedelta(datetime.now() - instance.publishing_time)

    def is_published(self, instance):
        if isinstance(instance, self.model):
            return instance.publishing_time < datetime.now()

    def first_deadline(self, instance):
        if isinstance(instance, self.model) and instance.first_deadline:
            return format_datetime(instance.first_deadline)



class AssignmentResource(AssignmentResourceMixin, BaseNodeInstanceResource):
    model = Assignment
    fields = ('id', 'parentnode', 'short_name', 'long_name', 'etag',
              'publishing_time', 'delivery_types', 'scale_points_percent',
              'is_published', 'publishing_time_offset_from_now',
              'first_deadline', 'anonymous', 'deadline_handling')

class AssignmentInstanceResource(AssignmentResourceMixin, BaseNodeInstanceResource):
    model = Assignment
    fields = AssignmentResource.fields + (
        'can_delete', 'admins', 'inherited_admins', 'breadcrumb', 'number_of_groups',
        'number_of_deliveries', 'number_of_groups_where_is_examiner', 'number_of_candidates',
        'gradingsystemplugin_title', 'has_valid_grading_setup',
        'max_points', 'passing_grade_min_points', 'points_to_grade_mapper',
        'grading_system_plugin_id')

    def _serialize_shortformat(self, config, shortformat):
        if shortformat:
            return {
                'widget': shortformat.widget,
                'shorthelp': unicode(shortformat.shorthelp(config))
            }
        else:
            return None

    def number_of_groups_where_is_examiner(self, instance):
        if isinstance(instance, self.model):
            return Examiner.objects.filter(
                user = self.view.request.user,
                assignmentgroup__parentnode=instance).count()

    def gradingsystemplugin_title(self, instance):
        if isinstance(instance, self.model):
            try:
                pluginapi = instance.get_gradingsystem_plugin_api()
            except GradingSystemPluginNotInRegistryError:
                return None
            else:
                return unicode(pluginapi.title)



class ListOrCreateAssignmentRest(BaseNodeListOrCreateView):
    """
    List the subjects where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)
    resource = AssignmentResource

    def authenticate_postrequest(self, user, parentnode_id):
        periodadmin_required(user, parentnode_id)

    def get_queryset(self):
        qry = super(ListOrCreateAssignmentRest, self).get_queryset()
        qry = qry.order_by('-publishing_time')
        return qry


class InstanceAssignmentRest(BaseNodeInstanceModelView):
    """
    This API provides read, update and delete on a single subject.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = AssignmentInstanceResource

    def get_queryset(self):
        qry = super(InstanceAssignmentRest, self).get_queryset()
        qry = qry.select_related('parentnode', 'parentnode__parentnode')
        qry = qry.prefetch_related('admins', 'admins__devilryuserprofile',
            'parentnode__admins', 'parentnode__admins__devilryuserprofile',
            'parentnode__parentnode__admins', 'parentnode__parentnode__admins__devilryuserprofile')
        qry = qry.annotate(number_of_groups=Count('assignmentgroups', distinct=True))
        qry = qry.annotate(number_of_deliveries=Count('assignmentgroups__deadlines__deliveries', distinct=True))
        qry = qry.annotate(number_of_candidates=Count('assignmentgroups__candidates', distinct=True))
        return qry
