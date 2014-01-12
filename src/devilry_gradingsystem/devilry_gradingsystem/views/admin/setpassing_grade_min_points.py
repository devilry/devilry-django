# from django.core.urlresolvers import reverse
# from django.shortcuts import redirect

from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from .base import AssignmentDetailView


class SetPassingGradeMinPointsView(AssignmentDetailView):
    template_name = 'devilry_gradingsystem/admin/setpassing_grade_min_points.django.html'
