from django.views.generic import TemplateView

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Period


class FrontpageView(TemplateView):
    template_name = 'devilry_student/frontpage.django.html'

    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)

        context['groups_waiting_for_deliveries'] = list(
            AssignmentGroup.objects\
                .filter_student_has_access(self.request.user)\
                .filter_is_active()\
                .filter_waiting_for_deliveries()\
                .select_related(
                    'last_deadline',
                    'parentnode', # Assignment
                    'parentnode__parentnode', # Period
                    'parentnode__parentnode__parentnode', # Subject
                )\
                .order_by('last_deadline__deadline')
        )
        context['active_periods'] = Period.objects\
            .filter_active()\
            .filter_is_candidate_or_relatedstudent(self.request.user)\
            .order_by('-start_time', 'parentnode__long_name', 'long_name')

        return context