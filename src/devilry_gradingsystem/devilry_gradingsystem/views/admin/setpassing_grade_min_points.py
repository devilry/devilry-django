from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django import forms

from devilry.apps.core.models import Assignment
from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from .base import AssignmentSingleObjectMixin


class PointsToGradeMapperForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['passing_grade_min_points']


class SetPassingGradeMinPointsView(AssignmentSingleObjectMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/setpassing_grade_min_points.django.html'

    def _get_next_page_url(self, passing_grade_min_points):
        assignment = self.object
        # TODO: Update
        return reverse('devilry_gradingsystem_admin_setmaxpoints', kwargs={
            'assignmentid': assignment.id,
        })

    def get(self, *args, **kwargs):
        passing_grade_min_points = self.request.GET.get('passing_grade_min_points')
        if passing_grade_min_points:
            self.object = self.get_object()
            assignment = self.object
            self.form = PointsToGradeMapperForm(self.request.GET, instance=assignment)
            if self.form.is_valid():
                self.form.save()
                return redirect(self._get_next_page_url(passing_grade_min_points))
        return super(SelectPluginView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SelectPluginView, self).get_context_data(**kwargs)
        context['pluginapi'] = assignment.get_gradingsystem_plugin_api()
        context['form'] = getattr(self, 'form', None)
        return context