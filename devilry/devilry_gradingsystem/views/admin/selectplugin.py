from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django import forms

from devilry.apps.core.models import Assignment
from devilry.devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from .base import AssignmentSingleObjectMixin


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['grading_system_plugin_id']

    def clean_grading_system_plugin_id(self):
        grading_system_plugin_id = self.cleaned_data['grading_system_plugin_id']
        if not grading_system_plugin_id in gradingsystempluginregistry:
            raise forms.ValidationError('Invalid grading system plugin ID: {}'.format(
                grading_system_plugin_id))
        return grading_system_plugin_id


class SelectPluginView(AssignmentSingleObjectMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/selectplugin.django.html'

    def _get_next_page_url(self, grading_system_plugin_id):
        assignment = self.object
        PluginApiClass = gradingsystempluginregistry.get(grading_system_plugin_id)
        pluginapi = PluginApiClass(assignment)
        if pluginapi.requires_configuration:
            return pluginapi.get_configuration_url()
        else:
            return reverse('devilry_gradingsystem_admin_setmaxpoints', kwargs={
                'assignmentid': assignment.id,
            })

    def get(self, *args, **kwargs):
        grading_system_plugin_id = self.request.GET.get('grading_system_plugin_id')
        if grading_system_plugin_id:
            self.object = self.get_object()
            assignment = self.object
            self.form = AssignmentForm(self.request.GET, instance=assignment)
            if self.form.is_valid():
                self.form.save()
                return redirect(self._get_next_page_url(grading_system_plugin_id))
        return super(SelectPluginView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SelectPluginView, self).get_context_data(**kwargs)
        # for plugin in gradingsystempluginregistry:
            # print unicode(plugin.title)
        context['pluginregistry'] = gradingsystempluginregistry.iter_with_assignment(self.object)
        context['form'] = getattr(self, 'form', None)
        return context
