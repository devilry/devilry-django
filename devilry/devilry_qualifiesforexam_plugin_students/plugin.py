# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy

from devilry.devilry_qualifiesforexam import plugintyperegistry
from .views import select_students


class StudentSelectPlugin(plugintyperegistry.PluginType):
    plugintypeid = 'devilry_qualifiesforexam_plugin_students.plugin_select_students'
    human_readable_name = ugettext_lazy('Manually select students')
    description = ugettext_lazy('Manually select the students that qualifies for exam.')

    def get_plugin_view_class(self):
        return select_students.PluginSelectStudentsView
