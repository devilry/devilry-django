from django.views.generic import TemplateView

from devilry.apps.core.models import Assignment


class DashboardView(TemplateView):
    template_name = "devilry_examiner/dashboard.django.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['active_assignments'] = Assignment.objects.filter_examiner_has_access(self.request.user).order_by('-publishing_time')
        return context
