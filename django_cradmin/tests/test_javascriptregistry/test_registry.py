from django import test

from django_cradmin import javascriptregistry


class JsComponent1(javascriptregistry.component.AbstractJsComponent):
    @classmethod
    def get_component_id(cls):
        return "jscomponent1"


class JsComponent2(javascriptregistry.component.AbstractJsComponent):
    @classmethod
    def get_component_id(cls):
        return "jscomponent2"


class TestRegistry(test.TestCase):
    def test_add_duplicate_component_id(self):
        class AnotherJsComponent1(javascriptregistry.component.AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "jscomponent1"

        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        with self.assertRaises(javascriptregistry.DuplicateComponentId):
            registry.add(AnotherJsComponent1)

    def test_add_ok(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        self.assertIn("jscomponent1", registry._jscomponent_classes)

    def test_contains_class_false(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        self.assertNotIn(JsComponent2, registry)

    def test_contains_class_true(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        self.assertIn(JsComponent1, registry)

    def test_contains_str_false(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        self.assertNotIn(JsComponent2.get_component_id(), registry)

    def test_contains_str_true(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        self.assertIn(JsComponent1.get_component_id(), registry)

    def test_getitem_failed(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        self.assertIn(JsComponent1.get_component_id(), registry)

    def test_getitem_ok(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        self.assertEqual(registry[JsComponent1.get_component_id()], JsComponent1)

    def test_get_component_objects_invalid_component_id(self):
        registry = javascriptregistry.MockableRegistry()
        with self.assertRaises(KeyError):
            registry.get_component_objects(request=None, component_ids=[JsComponent1.get_component_id()])

    def test_get_component_objects_simple(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        component_objects = registry.get_component_objects(
            request=None, component_ids=[JsComponent1.get_component_id()]
        )
        component_ids = [component.component_id for component in component_objects]
        self.assertEqual([JsComponent1.get_component_id()], component_ids)

    def test_get_component_objects_duplicates(self):
        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        component_objects = registry.get_component_objects(
            request=None, component_ids=[JsComponent1.get_component_id(), JsComponent1.get_component_id()]
        )
        component_ids = [component.component_id for component in component_objects]
        self.assertEqual([JsComponent1.get_component_id()], component_ids)

    def test_get_component_objects_with_dependencies(self):
        class MockJsComponent(javascriptregistry.component.AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "mock"

            def get_dependencies(self):
                return [JsComponent1.get_component_id(), JsComponent2.get_component_id()]

        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        registry.add(JsComponent2)
        registry.add(MockJsComponent)
        component_objects = registry.get_component_objects(
            request=None, component_ids=[MockJsComponent.get_component_id()]
        )
        component_ids = [component.component_id for component in component_objects]
        self.assertEqual(
            [
                JsComponent1.get_component_id(),
                JsComponent2.get_component_id(),
                MockJsComponent.get_component_id(),
            ],
            component_ids,
        )

    def test_get_component_objects_with_dependency_duplicates(self):
        class MockJsComponent1(javascriptregistry.component.AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "mock1"

            def get_dependencies(self):
                return [JsComponent1.get_component_id(), JsComponent2.get_component_id()]

        class MockJsComponent2(javascriptregistry.component.AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "mock2"

            def get_dependencies(self):
                return [JsComponent2.get_component_id()]

        registry = javascriptregistry.MockableRegistry()
        registry.add(JsComponent1)
        registry.add(JsComponent2)
        registry.add(MockJsComponent1)
        registry.add(MockJsComponent2)
        component_objects = registry.get_component_objects(
            request=None, component_ids=[MockJsComponent1.get_component_id(), MockJsComponent2.get_component_id()]
        )
        component_ids = [component.component_id for component in component_objects]
        self.assertEqual(
            [
                JsComponent1.get_component_id(),
                JsComponent2.get_component_id(),
                MockJsComponent1.get_component_id(),
                MockJsComponent2.get_component_id(),
            ],
            component_ids,
        )
