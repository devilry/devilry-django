from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django import forms

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import StaticFeedback
from devilry_gradingsystem.models import FeedbackDraft
from .base import AssignmentSingleObjectMixin


class SummaryView(AssignmentSingleObjectMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/summary.django.html'

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)
        assignment = self.object
        if assignment.grading_system_plugin_id:
            try:
                context['pluginapi'] = assignment.get_gradingsystem_plugin_api()
            except GradingSystemPluginNotInRegistryError:
                context['invalid_grading_system_plugin_id'] = True
        else:
            context['no_grading_system_plugin_id'] = True

        context['no_staticfeedbacks'] = not StaticFeedback.objects.filter(delivery__deadline__assignment_group__parentnode=assignment).exists()
        context['no_feedbackdrafts'] = not FeedbackDraft.objects.filter(delivery__deadline__assignment_group__parentnode=assignment).exists()
        return context