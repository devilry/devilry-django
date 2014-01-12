# from django.core.urlresolvers import reverse
# from django.shortcuts import redirect

from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from django.views.generic import View

from .base import AssignmentSingleObjectRequiresValidPluginMixin


class SelectPointsToGradeMapperView(View):
    template_name = 'devilry_gradingsystem/admin/select_points_to_grade_mapper.django.html'
