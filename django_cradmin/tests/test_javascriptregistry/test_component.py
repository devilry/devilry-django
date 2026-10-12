from django import test

from django_cradmin import javascriptregistry
from django_cradmin.javascriptregistry.component import AbstractJsComponent


class MinimalAbstractJsComponent(javascriptregistry.component.AbstractJsComponent):
    @classmethod
    def get_component_id(cls):
        return "minimal"


class TestAbstractJsComponent(test.TestCase):
    def test_get_component_id(self):
        with self.assertRaises(NotImplementedError):
            javascriptregistry.component.AbstractJsComponent.get_component_id()

    def test__init__component_id_uppercase_not_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "Hello"

        with self.assertRaises(javascriptregistry.component.ComponentIdFormatError):
            MockJsComponent(request=None)

    def test__init__component_id_minus_not_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "he-lo"

        with self.assertRaises(javascriptregistry.component.ComponentIdFormatError):
            MockJsComponent(request=None)

    def test__init__component_id_underscore_last_not_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "hello_"

        with self.assertRaises(javascriptregistry.component.ComponentIdFormatError):
            MockJsComponent(request=None)

    def test__init__component_id_underscore_first_not_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "_hello"

        with self.assertRaises(javascriptregistry.component.ComponentIdFormatError):
            MockJsComponent(request=None)

    def test__init__component_id_number_first_not_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "1hello"

        with self.assertRaises(javascriptregistry.component.ComponentIdFormatError):
            MockJsComponent(request=None)

    def test__init__component_id_underscore_middle_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "he_lo"

        MockJsComponent(request=None)  # No ComponentIdFormatError

    def test__init__component_id_number_middle_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "he3lo"

        MockJsComponent(request=None)  # No ComponentIdFormatError

    def test__init__component_id_number_last_allowed(self):
        class MockJsComponent(AbstractJsComponent):
            @classmethod
            def get_component_id(cls):
                return "hello1"

        MockJsComponent(request=None)  # No ComponentIdFormatError

    def test_get_dependencies(self):
        self.assertEqual([], MinimalAbstractJsComponent(request=None).get_dependencies())

    def test_get_head_sourceurls(self):
        self.assertEqual([], MinimalAbstractJsComponent(request=None).get_head_sourceurls())

    def test_get_sourceurls(self):
        self.assertEqual([], MinimalAbstractJsComponent(request=None).get_sourceurls())

    def test_get_javascript_code_before_sourceurls(self):
        self.assertIsNone(MinimalAbstractJsComponent(request=None).get_javascript_code_before_sourceurls())

    def test_get_javascript_code_after_sourceurls(self):
        self.assertIsNone(MinimalAbstractJsComponent(request=None).get_javascript_code_after_sourceurls())

    def test_get_static_url(self):
        self.assertEqual("/static/test", MinimalAbstractJsComponent(request=None).get_static_url(path="test"))
