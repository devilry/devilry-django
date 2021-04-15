# -*- coding: utf-8 -*-


# Devilry imports
from django.utils.translation import gettext_lazy

from devilry.devilry_qualifiesforexam.plugintyperegistry import PluginType
from .views import select_assignment


class SelectAssignmentsPlugin(PluginType):
    plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments'
    human_readable_name = gettext_lazy('Select assignments that must be approved')
    description = gettext_lazy(
        'Choose this option if you require your students to get a passing grade on the assignments '
        'you select. All assignments are selected by default.'
    )

    def get_plugin_view_class(self):
        return select_assignment.PluginSelectAssignmentsView
