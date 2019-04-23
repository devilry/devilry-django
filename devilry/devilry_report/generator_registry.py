from ievv_opensource.utils.singleton import Singleton


class Registry(Singleton):
    """
    Registry of devilry_report generator types.
    Holds exactly one subclass of :class:`devilry.devilry_report.abstract_generator.AbstractReportGenerator`
    for each `generator_type`.
    """
    def __init__(self):
        super(Registry, self).__init__()
        self._generator_type_classes = {}

    def __contains__(self, generator_type):
        """
        Implement "in"-operator support for ``Registry._generator_type_classes``.
        """
        return generator_type in self._generator_type_classes

    def __iter__(self):
        """
        Iterate over the registry yielding
        subclasses of :class:`devilry.devilry_report.abstract_generator.AbstractReportGenerator`.
        """
        return iter(list(self._generator_type_classes.values()))

    def get(self, generator_type):
        """
        Get a subclass of :class:`devilry.devilry_report.abstract_generator.AbstractReportGenerator` stored in the
        registry by the ``generator_type``.

        Args:
            generator_type (str): A
                :obj:`devilry.devilry_report.abstract_generator.AbstractReportGenerator.get_generator_type`.

        Raises:
            ValueError: If `generator_type` is not in the registry.
        """
        if generator_type not in self:
            raise ValueError('{} not in registry'.format(generator_type))
        return self._generator_type_classes[generator_type]

    def add(self, generator_class):
        """
        Add the provided ``generator_class`` to the registry.

        Args:
            generator_class: A subclass of
                :class:`devilry.devilry_report.abstract_generator.AbstractReportGenerator`.

        Raises:
            ValueError: When a generator class with the same
                :obj:`devilry.devilry_report.abstract_generator.AbstractReportGenerator.get_generator_type`
                already exists in the registry.
        """
        if generator_class.get_generator_type() in self:
            raise ValueError('{} already in registry'.format(generator_class.get_generator_type()))
        self._generator_type_classes[generator_class.get_generator_type()] = generator_class

    def remove(self, generator_type):
        """
        Remove a generator class with the provided `generator_type` from the registry.

        Args:
            generator_type (str): A
                :obj:`devilry.devilry_report.abstract_generator.AbstractReportGenerator.get_generator_type`.

        Raises:
            ValueError: If the generator_type does not exist in the registry.
        """
        if generator_type not in self:
            raise ValueError('{} not in registry'.format(generator_type))
        del self._generator_type_classes[generator_type]


class MockableRegistry(Registry):
    """
    A non-singleton version of :class:`Registry`. For tests.
    """
    def __init__(self):
        self._instance = None
        super(MockableRegistry, self).__init__()

    @classmethod
    def make_mockregistry(cls, *generator_classes):
        """
        Shortcut for making a mock registry.

        Typical usage in a test::

            from django import test
            from unittest import mock
            from devilry.devilry_report.generator import AbstractReportGenerator
            from devilry.devilry_report import generator_registry

            class TestSomething(test.TestCase):

                def test_something(self):
                    class Mock1(AbstractReportGenerator):
                        @classmethod get_generator_type(cls):
                            return 'mock1'

                    class Mock2(AbstractReportGenerator):
                        @classmethod get_generator_type(cls):
                            return 'mock2'

                    mockregistry = generator_registry.MockableRegistry.make_mockregistry(
                        Mock1, Mock2)

                    with mock.patch('devilry.devilry_report.generator_registry.Registry.get_instance',
                                    lambda: mockregistry):
                        pass  # Your test code here

        Args:
            *generator_classes: Zero or more
                :obj:`.devilry.devilry_report.abstract_generator.AbstractReportGenerator`
                subclasses.

        Returns:
            An object of this class with the requested generator_classes registered.
        """
        mockregistry = cls()
        for generator_class in generator_classes:
            mockregistry.add(generator_class=generator_class)
        return mockregistry
