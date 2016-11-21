# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from devilry.devilry_qualifiesforexam import plugintyperegistry
from .views import select_students


class StudentSelectPlugin(plugintyperegistry.PluginType):
    plugintypeid = 'devilry_qualifiesforexam_plugin_students.plugin_select_students'
    human_readable_name = 'Manually select students'
    description = 'Manually select the students that qualifies for exam.'

    def get_plugin_view_class(self):
        return select_students.PluginSelectStudentsView
