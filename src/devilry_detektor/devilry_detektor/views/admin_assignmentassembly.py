from django.views.generic.detail import DetailView

from devilry.apps.core.models import Assignment
from devilry_detektor.models import DetektorAssignment


class AssignmentAssemblyView(DetailView):
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'
    template_name = 'devilry_detektor/admin/assignmentassembly.django.html'

    def get_queryset(self):
        return Assignment.objects.filter_admin_has_access(self.request.user)\
            .select_related(
                'parentnode', # Period
                'parentnode__parentnode') # Subject

    def get_context_data(self, **kwargs):
        context = super(AssignmentAssemblyView, self).get_context_data(**kwargs)
        assignment = context['assignment']
        try:
            context['detektorassignment'] = assignment.detektorassignment
        except DetektorAssignment.DoesNotExist:
            pass
        return context
