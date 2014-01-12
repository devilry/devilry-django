from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django import forms

from devilry.apps.core.models import Assignment
from .base import AssignmentSingleObjectRequiresValidPluginMixin


class SetupCustomTableView(AssignmentSingleObjectRequiresValidPluginMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/setup_custom_table.django.html'


    def get(self, *args, **kwargs):
        return super(SetupCustomTableView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetupCustomTableView, self).get_context_data(**kwargs)
        #context['pluginapi'] = self.object.get_gradingsystem_plugin_api()
        #context['form'] = getattr(self, 'form', None)
        return context