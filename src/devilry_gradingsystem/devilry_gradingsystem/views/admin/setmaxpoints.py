# from django.core.urlresolvers import reverse
# from django.shortcuts import redirect

from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from .base import AssignmentDetailView


class SetMaxPointsView(AssignmentDetailView):
    template_name = 'devilry_gradingsystem/admin/setmaxpoints.django.html'
