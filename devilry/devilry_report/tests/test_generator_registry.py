# -*- coding: utf-8 -*-


import mock
from django import test

from devilry.devilry_report import abstract_generator
from devilry.devilry_report import generator_registry


class MockGenerator(abstract_generator.AbstractReportGenerator):
    @classmethod
    def get_generator_type(cls):
        return 'mock-generator'


class TestGeneratorRegistry(test.TestCase):
    def test_registry_get_ok(self):
        mockregistry = generator_registry.MockableRegistry.make_mockregistry(MockGenerator)
        with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                        lambda: mockregistry):
            self.assertEqual(mockregistry.get(MockGenerator.get_generator_type()), MockGenerator)

    def test_registry_get_does_not_exist(self):
        mockregistry = generator_registry.MockableRegistry.make_mockregistry()
        with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                        lambda: mockregistry):
            with self.assertRaisesMessage(ValueError, 'test-generator not in registry'):
                mockregistry.get('test-generator')

    def test_add_ok(self):
        mockregistry = generator_registry.MockableRegistry.make_mockregistry()
        with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                        lambda: mockregistry):
            mockregistry.add(MockGenerator)
            self.assertEqual(mockregistry.get(MockGenerator.get_generator_type()), MockGenerator)

    def test_add_already_exists(self):
        mockregistry = generator_registry.MockableRegistry.make_mockregistry(MockGenerator)
        with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                        lambda: mockregistry):
            with self.assertRaisesMessage(ValueError, 'mock-generator already in registry'):
                mockregistry.add(MockGenerator)

    def test_remove_ok(self):
        mockregistry = generator_registry.MockableRegistry.make_mockregistry(MockGenerator)
        with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                        lambda: mockregistry):
            mockregistry.remove(generator_type=MockGenerator.get_generator_type())
            self.assertFalse('mock-generator' in mockregistry)

    def test_remove_generator_does_not_exist(self):
        mockregistry = generator_registry.MockableRegistry.make_mockregistry()
        with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                        lambda: mockregistry):
            with self.assertRaisesMessage(ValueError, 'mock-generator not in registry'):
                mockregistry.remove(generator_type='mock-generator')

    def test_iterate(self):
        class MockGenerator1(abstract_generator.AbstractReportGenerator):
            @classmethod
            def get_generator_type(cls):
                return 'mock-generator1'

        class MockGenerator2(abstract_generator.AbstractReportGenerator):
            @classmethod
            def get_generator_type(cls):
                return 'mock-generator2'

        class MockGenerator3(abstract_generator.AbstractReportGenerator):
            @classmethod
            def get_generator_type(cls):
                return 'mock-generator3'

        mockregistry = generator_registry.MockableRegistry.make_mockregistry(
            MockGenerator1, MockGenerator2, MockGenerator3)
        with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                        lambda: mockregistry):
            generator_classes_list = [generator_class for generator_class in mockregistry]
            self.assertIn(MockGenerator1, generator_classes_list)
            self.assertIn(MockGenerator2, generator_classes_list)
            self.assertIn(MockGenerator3, generator_classes_list)
