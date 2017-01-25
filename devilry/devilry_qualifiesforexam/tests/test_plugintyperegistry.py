# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django import test

# Devilry imports
from devilry.devilry_qualifiesforexam import plugintyperegistry


class TestPluginSubclassFactory(test.TestCase):

    def test_create_subclass(self):
        testpluginclass = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
                str('TestPlugin'),
                plugintypeid='test_plugin',
                human_readable_name='Test plugin',
                description='Test plugin that does stuff')
        testplugin = testpluginclass()
        self.assertEquals('test_plugin', testplugin.get_plugintypeid())
        self.assertEquals('Test plugin', testplugin.get_human_readable_name())
        self.assertEquals('Test plugin that does stuff', testplugin.get_description())
        self.assertEquals(None, testplugin.get_plugin_view_class())


class TestPluginTypeRegistry(test.TestCase):

    def test_add_plugin(self):
        # Plugin is added to registry and check is performed to make sure it was added.
        testregistry = plugintyperegistry.MockableRegistry.make_mockregistry()
        testpluginclass = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
            classname=str('TestPlugin'),
            plugintypeid='test_plugin'
        )
        testregistry.add(testpluginclass)
        self.assertEquals('test_plugin', testregistry['test_plugin'].get_plugintypeid())

    def test_add_plugin_duplicate(self):
        # Registry should raise error if plugin with same plugintypeid is added.
        testregistry = plugintyperegistry.MockableRegistry.make_mockregistry()
        testpluginclass = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
                classname=str('TestPlugin'),
                plugintypeid='test_plugin'
        )
        testregistry.add(testpluginclass)

        with self.assertRaises(plugintyperegistry.DuplicatePluginTypeError):
            testregistry.add(testpluginclass)

    def test_iterate_plugins(self):
        # Iterate and make sure all plugins exist in registry
        testregistry = plugintyperegistry.MockableRegistry.make_mockregistry()
        testpluginclass1 = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
            classname=str('TestPlugin1'),
            plugintypeid='test_plugin1'
        )
        testpluginclass2 = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
            classname=str('TestPlugin2'),
            plugintypeid='test_plugin2'
        )
        testpluginclass3 = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
            classname=str('TestPlugin3'),
            plugintypeid='test_plugin3'
        )

        plugins = [testpluginclass1, testpluginclass2, testpluginclass3]

        testregistry.add(testpluginclass1)
        testregistry.add(testpluginclass2)
        testregistry.add(testpluginclass3)

        for plugin in testregistry:
            self.assertIn(plugin, plugins)
