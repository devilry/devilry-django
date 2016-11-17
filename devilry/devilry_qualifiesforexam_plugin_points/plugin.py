# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from devilry.devilry_qualifiesforexam.plugintyperegistry import PluginType
from .views import select_assignment_and_points


class PointsPlugin(PluginType):
    plugintypeid = 'devilry_qualifiesforexam_plugin_points.plugin_points'
    human_readable_name = 'Plugin for points to achieve on selected assignments'
    description = 'Choose the assignments that are qualifying and the score ' \
                  'that must be accumulated from the qualifying assignments'

    def get_plugin_view_class(self):
        return select_assignment_and_points.PluginSelectAssignmentsAndPointsView
