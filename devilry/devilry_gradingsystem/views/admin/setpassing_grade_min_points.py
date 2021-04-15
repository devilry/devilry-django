from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.views.generic import View
from django import forms
from django.utils.translation import gettext_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import ButtonHolder

from devilry.apps.core.models import Assignment
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginNotInRegistryError
from .base import AssignmentSingleObjectRequiresValidPluginMixin


class PassingGradeMinPointsForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['passing_grade_min_points']

    def __init__(self, *args, **kwargs):
        assignment = kwargs['instance']
        super(PassingGradeMinPointsForm, self).__init__(*args, **kwargs)

        if assignment.points_to_grade_mapper == 'custom-table':
            self.fields['passing_grade_min_points'] = forms.TypedChoiceField(
                label=gettext_lazy('Select the grade required to pass the assignment'),
                coerce=int,
                choices=assignment.get_point_to_grade_map().as_choices()
            )

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('passing_grade_min_points')
        )


class SetPassingGradeMinPointsCommonMixin(AssignmentSingleObjectRequiresValidPluginMixin):
    template_name = 'devilry_gradingsystem/admin/setpassing_grade_min_points.django.html'

    def get_pluginapi(self):
        assignment = self.get_object()
        try:
            return assignment.get_gradingsystem_plugin_api()
        except GradingSystemPluginNotInRegistryError:
            return None

    def add_common_context_data(self, context):
        context['pluginapi'] = self.get_pluginapi()
        context['current_step'] = self.get_wizard_step_map().get_by_slug('setpassing_grade_min_points')

    def get_success_url(self):
        return reverse('devilry_gradingsystem_admin_summary', kwargs={
            'assignmentid': self.object.id
        })


class SetPassingGradeMinPointsDisplay(SetPassingGradeMinPointsCommonMixin, DetailView):

    def get(self, *args, **kwargs):
        pluginapi = self.get_pluginapi()
        if pluginapi and pluginapi.sets_passing_grade_min_points_automatically:
            self.object = self.get_object()
            assignment = self.object
            assignment.set_passing_grade_min_points(pluginapi.get_passing_grade_min_points())
            assignment.full_clean()
            assignment.save()
            return redirect(str(self.get_success_url()))
        else:
            return super(SetPassingGradeMinPointsDisplay, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetPassingGradeMinPointsDisplay, self).get_context_data(**kwargs)
        self.add_common_context_data(context)
        context['form'] = PassingGradeMinPointsForm(instance=self.object)
        return context



class SetPassingGradeMinPointsUpdate(SetPassingGradeMinPointsCommonMixin, UpdateView):
    form_class = PassingGradeMinPointsForm

    def get_context_data(self, **kwargs):
        context = super(SetPassingGradeMinPointsUpdate, self).get_context_data(**kwargs)
        self.add_common_context_data(context)
        return context


class SetPassingGradeMinPointsView(View):
    def get(self, request, *args, **kwargs):
        view = SetPassingGradeMinPointsDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = SetPassingGradeMinPointsUpdate.as_view()
        return view(request, *args, **kwargs)
