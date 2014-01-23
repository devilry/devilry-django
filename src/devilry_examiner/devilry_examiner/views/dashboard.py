from collections import OrderedDict
from django.views.generic import TemplateView
from django.db.models import Count

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup


class DashboardView(TemplateView):
    template_name = "devilry_examiner/dashboard.django.html"


    def _add_statistics(self, assignment):
        assignment.count_waiting_for_feedback = AssignmentGroup.objects\
            .filter_examiner_has_access(self.request.user)\
            .filter(parentnode=assignment)\
            .filter_waiting_for_feedback()\
            .count()

        return assignment

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        active_assignments = Assignment.objects\
            .filter_examiner_has_access(self.request.user)\
            .order_by('-publishing_time')\
            .select_related('parentnode', 'parentnode__parentnode', 'examiners')\
            .annotate(count_total_groups=Count('assignmentgroups'))
        context['active_assignments'] = map(self._add_statistics, active_assignments)
        return context
