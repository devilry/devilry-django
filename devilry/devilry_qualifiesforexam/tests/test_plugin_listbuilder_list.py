# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 3rd party imports
from model_mommy import mommy

# Django imports
from django import test

# Devilry imports
from devilry.devilry_qualifiesforexam.listbuilder import plugin_listbuilder_list
from devilry.devilry_qualifiesforexam import plugintyperegistry


class TestPluginListBuilderList(test.TestCase):

    def test_listbuilder_item_value(self):
        # Check that the inneritem value of the frame is the same as the plugin added to the registry
        # the listbuilder_list is built from.
        plugintypeclass = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
            classname=str('TestPlugin'),
            plugintypeid='test_plugin'
        )
        testregistry = plugintyperegistry.MockableRegistry.make_mockregistry()
        testregistry.add(plugintypeclass)
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')

        listbuilder_list = plugin_listbuilder_list.PluginListBuilderList.from_plugin_registry(
                pluginregistry=testregistry,
                roleid=testperiod.id)

        self.assertEquals(plugintypeclass().get_plugintypeid(),
                          listbuilder_list.renderable_list[0].inneritem.value.get_plugintypeid())
