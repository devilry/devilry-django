from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django import forms

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import StaticFeedback
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginNotInRegistryError
from devilry.devilry_gradingsystem.models import FeedbackDraft
from .base import AssignmentSingleObjectMixin


class SummaryView(AssignmentSingleObjectMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/summary.django.html'

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)
        assignment = self.object
        if assignment.grading_system_plugin_id:
            context['has_valid_grading_setup'] = assignment.has_valid_grading_setup()
            try:
                context['pluginapi'] = assignment.get_gradingsystem_plugin_api()
            except GradingSystemPluginNotInRegistryError:
                pass
        else:
            context['no_grading_system_plugin_id'] = True
        context['has_staticfeedbacks'] = StaticFeedback.objects.filter(delivery__deadline__assignment_group__parentnode=assignment).exists()
        context['has_feedbackdrafts'] = FeedbackDraft.objects.filter(delivery__deadline__assignment_group__parentnode=assignment).exists()

        if assignment.subject.is_admin(self.request.user):
            context['is_subjectadmin'] = True
        elif assignment.period.is_admin(self.request.user):
            context['is_periodadmin'] = True
        return context
