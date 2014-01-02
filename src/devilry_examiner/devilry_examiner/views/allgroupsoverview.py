from django.views.generic import DetailView

from devilry.apps.core.models import Assignment


class AllGroupsOverview(DetailView):
    template_name = "devilry_examiner/allgroupsoverview.django.html"
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'

    def get_queryset(self):
        if self.request.GET.get('waiting_for_feedback'):
            return Assignment.objects.filter_examiner_has_access(self.request.user).filter_by_status('waiting-for-feedback')
        elif self.request.GET.get('corrected'):
            return Assignment.objects.filter_examiner_has_access(self.request.user).filter_by_status('corrected')
        elif self.request.GET.get('waiting_for_deliveries'):
            return Assignment.objects.filter_examiner_has_access(self.request.user).filter_by_status('waiting-for-deliveries')
        else:
            return Assignment.objects.filter_examiner_has_access(self.request.user)
