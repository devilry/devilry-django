import htmls
from django import test

from unittest import mock
from django_cradmin.viewhelpers import listbuilder


class TestTitleDescription(test.TestCase):
    def test_title(self):
        rendered = listbuilder.itemvalue.TitleDescription(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual(
            "testvalue", selector.one(".test-cradmin-listbuilder-title-description__title").alltext_normalized
        )

    def test_without_description(self):
        rendered = listbuilder.itemvalue.TitleDescription(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertFalse(selector.exists(".test-cradmin-listbuilder-title-description__description"))

    def test_with_description(self):
        class MyEditDelete(listbuilder.itemvalue.TitleDescription):
            def get_description(self):
                return "The description"

        rendered = MyEditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual(
            "The description",
            selector.one(".test-cradmin-listbuilder-title-description__description").alltext_normalized,
        )


class MockValue(object):
    def __init__(self, value_str, pk):
        self.value_str = value_str
        self.pk = pk

    def __str__(self):
        return self.value_str


class TestUseThis(test.TestCase):
    def __make_mock_value(self, value_str, value_pk=1):
        # mockvalue = mock.MagicMock()
        # mockvalue.__str__.return_value = value_str
        # mockvalue.pk = value_pk
        # return mockvalue
        return MockValue(value_str=value_str, pk=value_pk)

    def __make_mock_request(self):
        mockrequest = mock.MagicMock()
        mockrequest.GET.__getitem__.return_value = "mocked"
        return mockrequest

    def test_title(self):
        rendered = listbuilder.itemvalue.UseThis(value=self.__make_mock_value("testvalue")).render(
            request=self.__make_mock_request()
        )
        selector = htmls.S(rendered)
        self.assertEqual(
            "testvalue", selector.one(".test-cradmin-listbuilder-title-description__title").alltext_normalized
        )

    def test_without_description(self):
        rendered = listbuilder.itemvalue.UseThis(value=self.__make_mock_value("testvalue")).render(
            request=self.__make_mock_request()
        )
        selector = htmls.S(rendered)
        self.assertFalse(selector.exists(".test-cradmin-listbuilder-title-description__description"))

    def test_with_description(self):
        class MyEditDelete(listbuilder.itemvalue.UseThis):
            def get_description(self):
                return "The description"

        rendered = MyEditDelete(value=self.__make_mock_value("testvalue")).render(request=self.__make_mock_request())
        selector = htmls.S(rendered)
        self.assertEqual(
            "The description",
            selector.one(".test-cradmin-listbuilder-title-description__description").alltext_normalized,
        )

    def test_preview_label(self):
        rendered = listbuilder.itemvalue.UseThis(value=self.__make_mock_value("testvalue")).render(
            request=self.__make_mock_request()
        )
        selector = htmls.S(rendered)
        self.assertEqual(
            "Select", selector.one(".django-cradmin-listbuilder-itemvalue-usethis-usethis-button").alltext_normalized
        )

    def test_preview_aria_label(self):
        rendered = listbuilder.itemvalue.UseThis(value=self.__make_mock_value("testvalue")).render(
            request=self.__make_mock_request()
        )
        selector = htmls.S(rendered)
        self.assertEqual(
            'Select "testvalue"',
            selector.one(".django-cradmin-listbuilder-itemvalue-usethis-usethis-button")["aria-label"],
        )


class TestEditDelete(test.TestCase):
    def test_title(self):
        rendered = listbuilder.itemvalue.EditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual(
            "testvalue", selector.one(".test-cradmin-listbuilder-title-description__title").alltext_normalized
        )

    def test_without_description(self):
        rendered = listbuilder.itemvalue.EditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertFalse(selector.exists(".test-cradmin-listbuilder-title-description__description"))

    def test_with_description(self):
        class MyEditDelete(listbuilder.itemvalue.EditDelete):
            def get_description(self):
                return "The description"

        rendered = MyEditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual(
            "The description",
            selector.one(".test-cradmin-listbuilder-title-description__description").alltext_normalized,
        )

    def test_edit_label(self):
        rendered = listbuilder.itemvalue.EditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual("Edit", selector.one(".test-cradmin-listbuilder-edit-delete__editbutton").alltext_normalized)

    def test_edit_aria_label(self):
        rendered = listbuilder.itemvalue.EditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual(
            'Edit "testvalue"', selector.one(".test-cradmin-listbuilder-edit-delete__editbutton")["aria-label"]
        )

    def test_delete_label(self):
        rendered = listbuilder.itemvalue.EditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual(
            "Delete", selector.one(".test-cradmin-listbuilder-edit-delete__deletebutton").alltext_normalized
        )

    def test_delete_aria_label(self):
        rendered = listbuilder.itemvalue.EditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertEqual(
            'Delete "testvalue"', selector.one(".test-cradmin-listbuilder-edit-delete__deletebutton")["aria-label"]
        )

    def test_viewbutton_not_rendered(self):
        rendered = listbuilder.itemvalue.EditDelete(value="testvalue").render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertFalse(selector.exists(".test-cradmin-listbuilder-edit-delete__previewbutton"))


class TestEditDeleteWithPreview(test.TestCase):
    def test_preview_label(self):
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_app.reverse_appurl.return_value = "/preview"
        rendered = listbuilder.itemvalue.EditDeleteWithPreview(value="testvalue").render(request=mockrequest)
        selector = htmls.S(rendered)
        self.assertEqual(
            "View", selector.one(".test-cradmin-listbuilder-edit-delete__previewbutton").alltext_normalized
        )

    def test_preview_aria_label(self):
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_app.reverse_appurl.return_value = "/preview"
        rendered = listbuilder.itemvalue.EditDeleteWithPreview(value="testvalue").render(request=mockrequest)
        selector = htmls.S(rendered)
        self.assertEqual(
            'View "testvalue"', selector.one(".test-cradmin-listbuilder-edit-delete__previewbutton")["aria-label"]
        )
