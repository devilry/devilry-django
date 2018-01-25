# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from django.utils.translation import ugettext_lazy

from devilry.devilry_qualifiesforexam.plugintyperegistry import PluginType
from .views import select_assignment_and_points


class PointsPlugin(PluginType):
    plugintypeid = 'devilry_qualifiesforexam_plugin_points.plugin_points'
    human_readable_name = ugettext_lazy('Points to achieve on selected assignments')
    description = ugettext_lazy(
        'Choose the total sum of points that needs to be achieved for the '
        'selected assignments. All assignments are selected by default.'
    )

    def get_plugin_view_class(self):
        return select_assignment_and_points.PluginSelectAssignmentsAndPointsView
