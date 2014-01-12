from django.views.generic.detail import SingleObjectMixin
from django.http import Http404

from devilry.apps.core.models import Assignment
from devilry_gradingsystem.pluginregistry import GradingSystemPluginNotInRegistryError


class AssignmentSingleObjectMixin(SingleObjectMixin):
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter_admin_has_access(self.request.user)\
            .select_related(
                'parentnode', # Period
                'parentnode__parentnode') # Subject


class AssignmentSingleObjectRequiresValidPluginMixin(AssignmentSingleObjectMixin):
    def get_object(self):
        assignment = super(AssignmentSingleObjectRequiresValidPluginMixin, self).get_object()
        try:
            assignment.get_gradingsystem_plugin_api()
        except GradingSystemPluginNotInRegistryError:
            raise Http404()
        return assignment