from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django import forms

from devilry.apps.core.models import Assignment
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
        return context