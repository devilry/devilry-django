from model_bakery import baker

from cradmin_legacy.python2_compatibility import mock
import htmls
from django.test import TestCase
from django.test.client import RequestFactory
from django import http
from django import forms

from cradmin_legacy.tests.viewhelpers.cradmin_viewhelpers_testapp.models import TestModel
from cradmin_legacy.viewhelpers import multiselect

TEST_PK = 42


class DemoForm(forms.Form):
    data = forms.CharField()


class SimpleMultiSelectFormView(multiselect.MultiSelectFormView):
    form_class = DemoForm
    model = TestModel

    def get_queryset_for_role(self, role):
        return TestModel.objects.all()

    def form_valid(self, form):
        return http.HttpResponse("Submitted: {data}".format(**form.cleaned_data))

    def get_field_layout(self):
        return ["data"]


class SimpleMultiSelectView(multiselect.MultiSelectView):
    def get_queryset_for_role(self, role):
        return TestModel.objects.all()

    def object_selection_valid(self):
        return http.HttpResponse("OK")


class TestMultiSelectView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.testmodelinstance = baker.make("cradmin_viewhelpers_testapp.TestModel", pk=TEST_PK)

    def test_object_selection_valid(self):
        testmodelinstance2 = baker.make("cradmin_viewhelpers_testapp.TestModel")
        testmodelinstance3 = baker.make("cradmin_viewhelpers_testapp.TestModel")

        request = self.factory.post("/test", {"selected_objects": [testmodelinstance2.id, testmodelinstance3.id]})
        request.cradmin_role = mock.MagicMock()
        response = SimpleMultiSelectView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_object_selection_invalid(self):
        request = self.factory.post("/test", {"selected_objects": [1, 10]})
        request.cradmin_role = mock.MagicMock()
        response = SimpleMultiSelectView.as_view()(request)
        selector = htmls.S(response.content)
        self.assertEqual(
            selector.one(".alert.alert-danger").text_normalized,
            "Invalid selection. This is usually caused by someone else changing permissions "
            "while you where selecting items to edit.",
        )

    def test_object_selection_invalid_override(self):
        class SimpleMultiSelectViewOverride(SimpleMultiSelectView):
            def object_selection_invalid(self, form):
                return http.HttpResponse("Invalid selection")

        request = self.factory.post("/test", {"selected_objects": [1, 10]})
        request.cradmin_role = mock.MagicMock()
        response = SimpleMultiSelectViewOverride.as_view()(request)
        self.assertIn(b"Invalid selection", response.content)


class TestMultiSelectFormView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.testmodelinstance = baker.make("cradmin_viewhelpers_testapp.TestModel", pk=TEST_PK)

    def test_first_load(self):

        request = self.factory.post(
            "/test", {"selected_objects": [self.testmodelinstance.id], "is_the_multiselect_form": "yes"}
        )
        request.cradmin_role = mock.MagicMock()
        response = SimpleMultiSelectFormView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count("#cradmin_legacy_contentwrapper form"), 1)
        self.assertEqual(selector.one("input[name=selected_objects]")["type"], "hidden")
        self.assertEqual(selector.one("input[name=selected_objects]")["value"], f"{self.testmodelinstance.id}")
        self.assertEqual(selector.count("input[name=data]"), 1)
        self.assertFalse(selector.exists("form .has-error"))

    def test_form_invalid(self):

        request = self.factory.post(
            "/test",
            {
                "selected_objects": [self.testmodelinstance.id],
            },
        )
        request.cradmin_role = mock.MagicMock()
        response = SimpleMultiSelectFormView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count("#cradmin_legacy_contentwrapper form"), 1)
        self.assertEqual(selector.one("input[name=selected_objects]")["type"], "hidden")
        self.assertEqual(selector.one("input[name=selected_objects]")["value"], f"{self.testmodelinstance.id}")
        self.assertEqual(selector.count("input[name=data]"), 1)
        self.assertEqual(selector.one("#div_id_data .help-block").alltext_normalized, "This field is required.")

    def test_form_valid(self):

        request = self.factory.post("/test", {"selected_objects": [self.testmodelinstance.id], "data": "Hello world"})
        request.cradmin_role = mock.MagicMock()
        response = SimpleMultiSelectFormView.as_view()(request)
        self.assertEqual(response.content, b"Submitted: Hello world")

    def test_form_valid_success_redirect(self):
        class DemoForm(forms.Form):
            data = forms.CharField()

        class SimpleMultiSelectFormView(multiselect.MultiSelectFormView):
            form_class = DemoForm
            model = TestModel

            def get_queryset_for_role(self, role):
                return TestModel.objects.filter(id=TEST_PK)

            def get_success_url(self):
                return "/success"

            def form_valid(self, form):
                return self.success_redirect_response()

        request = self.factory.post("/test", {"selected_objects": [self.testmodelinstance.id], "data": "Hello world"})
        request.cradmin_role = mock.MagicMock()
        response = SimpleMultiSelectFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/success")
