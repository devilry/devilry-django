from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django import forms

from devilry.apps.core.models import Assignment
from .base import AssignmentSingleObjectRequiresValidPluginMixin


class PointsToGradeMapperForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['points_to_grade_mapper']


class SelectPointsToGradeMapperView(AssignmentSingleObjectRequiresValidPluginMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/select_points_to_grade_mapper.django.html'

    def _get_next_page_url(self, points_to_grade_mapper):
        assignment = self.object
        pluginapi = assignment.get_gradingsystem_plugin_api()
        if points_to_grade_mapper == 'custom-table':
            return reverse('devilry_gradingsystem_admin_setup_custom_table', kwargs={
                'assignmentid': assignment.id,
            })
        else:
            return reverse('devilry_gradingsystem_admin_setpassing_grade_min_points', kwargs={
                'assignmentid': assignment.id,
            })

    def get(self, *args, **kwargs):
        points_to_grade_mapper = self.request.GET.get('points_to_grade_mapper')
        if points_to_grade_mapper:
            self.object = self.get_object()
            assignment = self.object
            self.form = PointsToGradeMapperForm(self.request.GET, instance=assignment)
            if self.form.is_valid():
                self.form.save()
                return redirect(self._get_next_page_url(points_to_grade_mapper))
        return super(SelectPointsToGradeMapperView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SelectPointsToGradeMapperView, self).get_context_data(**kwargs)
        context['pluginapi'] = self.object.get_gradingsystem_plugin_api()
        context['form'] = getattr(self, 'form', None)
        context['current_step'] = self.get_wizard_step_map().get_by_slug('select_points_to_grade_mapper')
        return context