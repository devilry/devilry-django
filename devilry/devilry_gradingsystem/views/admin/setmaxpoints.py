from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.views.generic import View
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import HTML
from crispy_forms.layout import ButtonHolder

from devilry.apps.core.models import Assignment
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginNotInRegistryError
from .base import AssignmentSingleObjectRequiresValidPluginMixin


class MaxPointsForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['max_points']

    def __init__(self, *args, **kwargs):
        super(MaxPointsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('max_points')
        )


class SetMaxPointsComminMixin(AssignmentSingleObjectRequiresValidPluginMixin):
    template_name = 'devilry_gradingsystem/admin/setmaxpoints.django.html'

    def get_pluginapi(self):
        assignment = self.get_object()
        try:
            return assignment.get_gradingsystem_plugin_api()
        except GradingSystemPluginNotInRegistryError:
            return None

    def add_common_context_data(self, context):
        pluginapi = self.get_pluginapi()
        context['pluginapi'] = pluginapi
        context['current_step'] = self.get_wizard_step_map().get_by_slug('setmaxpoints')

    def get_success_url(self):
        return reverse('devilry_gradingsystem_admin_select_points_to_grade_mapper', kwargs={
            'assignmentid': self.object.id
        })


class SetMaxPointsDisplay(SetMaxPointsComminMixin, DetailView):

    def get(self, *args, **kwargs):
        pluginapi = self.get_pluginapi()
        if pluginapi and pluginapi.sets_max_points_automatically:
            self.object = self.get_object()
            assignment = self.object
            assignment.set_max_points(pluginapi.get_max_points())
            assignment.full_clean()
            assignment.save()
            return redirect(str(self.get_success_url()))
        else:
            return super(SetMaxPointsDisplay, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetMaxPointsDisplay, self).get_context_data(**kwargs)
        self.add_common_context_data(context)
        context['form'] = MaxPointsForm(instance=self.object)
        return context



class SetMaxPointsUpdate(SetMaxPointsComminMixin, UpdateView):
    form_class = MaxPointsForm

    def get_context_data(self, **kwargs):
        context = super(SetMaxPointsUpdate, self).get_context_data(**kwargs)
        self.add_common_context_data(context)
        return context


class SetMaxPointsView(View):
    def get(self, request, *args, **kwargs):
        view = SetMaxPointsDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = SetMaxPointsUpdate.as_view()
        return view(request, *args, **kwargs)
