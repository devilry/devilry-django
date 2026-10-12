import htmls
from django import test

from cradmin_legacy import python2_compatibility
from cradmin_legacy.viewhelpers.multiselect2 import selected_item_renderer
from cradmin_legacy.python2_compatibility import mock


class TestSelectedItem(test.TestCase):
    def test_title(self):
        mockvalue = mock.MagicMock()
        mockvalue.__str__.return_value = "testvalue"
        if python2_compatibility.is_python2():
            mockvalue.__unicode__.return_value = "testvalue"
        selector = htmls.S(selected_item_renderer.SelectedItem(value=mockvalue).render())
        self.assertEqual(
            "testvalue", selector.one(".cradmin-legacy-multiselect2-target-selected-item-title").alltext_normalized
        )

    def test_no_description(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(selected_item_renderer.SelectedItem(value=mockvalue).render())
        self.assertFalse(selector.exists(".cradmin-legacy-multiselect2-target-selected-item-description"))

    def test_has_description(self):
        class MySelectedItem(selected_item_renderer.SelectedItem):
            def get_description(self):
                return "test description"

        mockvalue = mock.MagicMock()
        selector = htmls.S(MySelectedItem(value=mockvalue).render())
        self.assertEqual(
            "test description",
            selector.one(".cradmin-legacy-multiselect2-target-selected-item-description").alltext_normalized,
        )

    def test_input_field(self):
        mockvalue = mock.MagicMock()
        mockvalue.pk = 10
        selector = htmls.S(selected_item_renderer.SelectedItem(value=mockvalue).render())
        self.assertEqual("10", selector.one('input[name="selected_items"]')["value"])

    def test_custom_input_field_name(self):
        class MySelectedItem(selected_item_renderer.SelectedItem):
            def get_inputfield_name(self):
                return "testfield"

        mockvalue = mock.MagicMock()
        selector = htmls.S(MySelectedItem(value=mockvalue).render())
        self.assertTrue(selector.exists('input[name="testfield"]'))

    def test_deselectbutton_text(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(selected_item_renderer.SelectedItem(value=mockvalue).render())
        self.assertEqual("Deselect", selector.one("button").alltext_normalized)

    def test_deselectbutton_aria_label(self):
        mockvalue = mock.MagicMock()
        mockvalue.__str__.return_value = "testvalue"
        if python2_compatibility.is_python2():
            mockvalue.__unicode__.return_value = "testvalue"
        selector = htmls.S(selected_item_renderer.SelectedItem(value=mockvalue).render())
        self.assertEqual('Deselect "testvalue"', selector.one("button")["aria-label"])
