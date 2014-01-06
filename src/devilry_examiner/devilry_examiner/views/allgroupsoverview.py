from django.views.generic import DetailView
from django.views.generic import TemplateView

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup


class AllGroupsOverview(DetailView):
    template_name = "devilry_examiner/allgroupsoverview_base.django.html"
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'

    def get_context_data(self, **kwargs):
        context = super(AllGroupsOverview, self).get_context_data(**kwargs)

        # Need to get queryset from custom manager.
        # Get only AssignmentGroup within same assignment
        groups = AssignmentGroup.objects.get_queryset().filter(parentnode__id=self.object.id)
        groups = groups.filter_examiner_has_access(self.request.user)

        context['groups'] = groups
        return context

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)


class WaitingForFeedbackOverview(AllGroupsOverview):
    template_name = "devilry_examiner/waiting-for-feedback-list.django.html"

    def get_context_data(self, **kwargs):
        context = super(WaitingForFeedbackOverview, self).get_context_data(**kwargs)

        # Need to get queryset from custom manager.
        # Get only AssignmentGroup within same assignment
        groups = AssignmentGroup.objects.get_queryset().filter(parentnode__id=self.object.id)
        groups = groups.filter_examiner_has_access(self.request.user).filter_by_status('waiting-for-feedback')

        context['groups'] = groups
        # context['groups'].filter_by_status('corrected')

        return context
