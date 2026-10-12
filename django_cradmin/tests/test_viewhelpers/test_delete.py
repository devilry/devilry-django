import htmls
from django.test import TestCase
from django.test.client import RequestFactory
from unittest import mock
from django_cradmin.viewhelpers import formview


class TestDelete(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get(self):
        class SimpleDeleteView(formview.WithinRoleDeleteView):
            def get_queryset_for_role(self):
                queryset = mock.MagicMock()
                return queryset

            def get_object(self, queryset=None):
                obj = mock.MagicMock()
                obj.__str__.return_value = "Simple Test Item"
                obj._meta = mock.MagicMock()
                obj._meta.verbose_name = "TestModel"
                return obj

        request = self.factory.get("/test")
        request.cradmin_app = mock.MagicMock()
        request.cradmin_instance = mock.MagicMock()
        response = SimpleDeleteView.as_view()(request, pk=10)
        response.render()
        selector = htmls.S(response.content)

        self.assertEqual(selector.one("form")["action"], "http://testserver/test")
        self.assertEqual(selector.one("h1.test-primary-h1").alltext_normalized, "Confirm delete")
        self.assertEqual(
            selector.one(".test-confirm-message").alltext_normalized,
            'Are you sure you want to delete "Simple Test Item"?',
        )

    def test_post(self):
        obj = mock.MagicMock()

        class SimpleDeleteView(formview.WithinRoleDeleteView):
            def get_queryset_for_role(self):
                queryset = mock.MagicMock()
                return queryset

            def get_object(self, queryset=None):
                return obj

        request = self.factory.post("/test")
        request._messages = mock.MagicMock()
        request.cradmin_app = mock.MagicMock()
        request.cradmin_app.reverse_appindexurl.return_value = "/success"
        SimpleDeleteView.as_view()(request, pk=10)
        obj.delete.assert_called_once_with()
