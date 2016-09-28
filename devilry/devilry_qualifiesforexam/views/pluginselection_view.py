# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.utils.translation import pgettext_lazy
from django.views.generic import TemplateView

# Devilry imports
from devilry.devilry_qualifiesforexam.listbuilder import plugin_listbuilder_list
from devilry.devilry_qualifiesforexam import plugintyperegistry


class SelectPluginView(TemplateView):
    """

    """
    template_name = 'devilry_qualifiesforexam/selectplugin.django.html'

    def get_queryset(self):
        return self.request.cradmin_instance.get_rolequeryset()

    def get_plugin_listbuilder_list(self):
        """
        Get a plugin listbuilder list.
        This function is mostly used for patching in tests.
        Override this to use a mockable registry for testing.

        Returns:
            List:
                A :class:`devilry.devilry_qualifiesforexam.listbuilder import plugin_listbuilder_list.PluginListBuilderList`.
        """
        listbuilder_class = plugin_listbuilder_list.PluginListBuilderList
        return listbuilder_class.from_plugin_registry(plugintyperegistry.Registry.get_instance(),
                                                      roleid=self.request.cradmin_role.id)

    def get_context_data(self, **kwargs):
        context_data = super(SelectPluginView, self).get_context_data(**kwargs)
        context_data['devilry_role'] = self.request.cradmin_instance.is_admin()
        context_data['headline'] = 'How do students qualify for final exams?'
        context_data['help_text'] = 'Select one of the options from the list. Each option starts a wizard ' \
                                    'that ends with a preview of the results before you get the option to save'
        context_data['plugin_listbuilder_list'] = self.get_plugin_listbuilder_list()

        return context_data
