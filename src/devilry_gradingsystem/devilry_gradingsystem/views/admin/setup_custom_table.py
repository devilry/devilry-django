# from django.core.urlresolvers import reverse
# from django.shortcuts import redirect

from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from .base import AssignmentDetailView


class SetupCustomTableView(AssignmentDetailView):
    template_name = 'devilry_gradingsystem/admin/setup_custom_table.django.html'
