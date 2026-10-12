# -*- coding: utf-8 -*-
import inspect

from ievv_opensource.utils.singleton import Singleton

from django_cradmin.javascriptregistry.component import AbstractJsComponent


class DuplicateComponentId(Exception):
    """
    Raised by :meth:`.Registry.add` if adding a component_id that is
    already in the registry.
    """


class Registry(Singleton):
    """
    Registry of :class:`.JsComponent` objects.

    Examples:

        First, define a subclass of :class:`~django_cradmin.javascriptregistry.component.AbstractJsComponent`.
        Then register the javascript component in the registry via an AppConfig for your
        Django app::

            from django.apps import AppConfig
            from django_cradmin import javascriptregistry

            class MyJsComponent(javascriptregistry.component.AbstractJsComponent):
                @classmethod
                def get_component_id(cls):
                    return 'my_cool_app'

                def get_head_sourceurls(self):
                    return [
                        self.get_static_url('myapp/js/myapp.js')
                    ]

            class MyAppConfig(AppConfig):
                name = 'myapp'

                def ready(self):
                    javascriptregistry.Registry.get_instance().add(jscomponent_class=MyJsComponent)
    """

    def __init__(self):
        super(Registry, self).__init__()
        self._jscomponent_classes = {}

    def add(self, jscomponent_class):
        """
        Add the given ``jscomponent_class`` to the registry.

        Parameters:
            jscomponent_class (django_cradmin.javascriptregistry.component.AbstractJsComponent):
                The javascript component class to add
                to the registry.
        """
        if jscomponent_class.get_component_id() in self._jscomponent_classes:
            raise DuplicateComponentId(
                "Duplicate component ID in javascriptregistry: {}".format(jscomponent_class.get_component_id())
            )
        self._jscomponent_classes[jscomponent_class.get_component_id()] = jscomponent_class

    def remove_if_exists(self, jscomponent_id):
        """
        Check if the provided component ID is in the registry
        and deletes it if found.

        Args:
            - jscomponent_id: String
        """
        if jscomponent_id in self._jscomponent_classes:
            del self._jscomponent_classes[jscomponent_id]

    def __contains__(self, component_id_or_object):
        """
        Check if the provided component ID, component object or
        component class is in the registry.

        Args:
            component_id_or_object: Can be a
                :class:`~django_cradmin.javascriptregistry.component.AbstractJsComponent` object,
                or a string.
        """
        if inspect.isclass(component_id_or_object) and issubclass(component_id_or_object, AbstractJsComponent):
            component_id = component_id_or_object.get_component_id()
        else:
            component_id = component_id_or_object
        return component_id in self._jscomponent_classes

    def __getitem__(self, component_id):
        """
        Get the :class:`~django_cradmin.javascri~ptregistry.component.AbstractJsComponent`
        class registered with ``component_id``.
        """
        return self._jscomponent_classes[component_id]

    def _get_component_object(self, request, component_id):
        component_class = self._jscomponent_classes[component_id]
        component = component_class(request=request)
        return component

    def _get_all_dependencies_for_component(self, request, component):
        all_dependencies = []
        for component_id in component.get_dependencies():
            component = self._get_component_object(request=request, component_id=component_id)
            all_dependencies.append(component)
            all_dependencies.extend(self._get_all_dependencies_for_component(request=request, component=component))
        return all_dependencies

    def get_component_objects(self, request, component_ids):
        """
        Get the :class:`~django_cradmin.javascri~ptregistry.component.AbstractJsComponent`
        objects for all the provided ``component_ids``, including all their
        dependencies (see :class:`~django_cradmin.javascri~ptregistry.component.AbstractJsComponent.get_dependencies`).

        Args:
            request: A :class:`django.http.HttpRequest` object.
            component_ids: An iterable of component IDs.

        Raises:
            KeyError: If any of the component IDs is not in the registry.

        Returns:
            list: A list of component objects.
        """
        added_component_ids = set()
        components = []

        for requested_component_id in component_ids:
            if requested_component_id in added_component_ids:
                continue

            requested_component = self._get_component_object(request=request, component_id=requested_component_id)
            for dependency_component in self._get_all_dependencies_for_component(
                request=request, component=requested_component
            ):
                dependency_component_id = dependency_component.__class__.get_component_id()
                if dependency_component_id in added_component_ids:
                    continue
                components.append(dependency_component)
                added_component_ids.add(dependency_component_id)

            components.append(requested_component)
            added_component_ids.add(requested_component_id)

        return components


class MockableRegistry(Registry):
    """
    A non-singleton version of :class:`.Registry`. For tests.

    Typical usage in a test::

        from django_cradmin import javascriptregistry

        class MockJsComponent(javascriptregistry.component.AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return 'mock_js_component'

        mockregistry = javascriptregistry.MockableRegistry()
        mockregistry.add(MockJsComponent)

        with mock.patch('django_cradmin.javascriptregistry.registry.Registry.get_instance',
                        lambda: mockregistry):
            pass  # ... your code here ...
    """

    def __init__(self):
        self._instance = None  # Ensure the singleton-check is not triggered
        super(MockableRegistry, self).__init__()
