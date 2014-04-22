from django.views.generic import TemplateView

from devilry.apps.core.models import AssignmentGroup


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

        return context