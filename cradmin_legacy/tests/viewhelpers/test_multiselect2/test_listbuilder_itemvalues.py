import json

import htmls
from django import test

from cradmin_legacy import python2_compatibility
from cradmin_legacy.viewhelpers.multiselect2 import listbuilder_itemvalues
from cradmin_legacy.python2_compatibility import mock


class TestItemValue(test.TestCase):
    def test_title(self):
        mockvalue = mock.MagicMock()
        mockvalue.__str__.return_value = "testvalue"
        if python2_compatibility.is_python2():
            mockvalue.__unicode__.return_value = "testvalue"

        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue).render())
        self.assertEqual(
            "testvalue", selector.one(".cradmin-legacy-listbuilder-itemvalue-titledescription-title").alltext_normalized
        )

    def test_no_description(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue).render())
        self.assertFalse(selector.exists(".cradmin-legacy-listbuilder-itemvalue-titledescription-description"))

    def test_has_description(self):
        class MySelectedItem(listbuilder_itemvalues.ItemValue):
            def get_description(self):
                return "test description"

        mockvalue = mock.MagicMock()
        selector = htmls.S(MySelectedItem(value=mockvalue).render())
        self.assertEqual(
            "test description",
            selector.one(".cradmin-legacy-listbuilder-itemvalue-titledescription-description").alltext_normalized,
        )

    def test_selectbutton_text(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue).render())
        self.assertEqual(
            "Select", selector.one("button.cradmin-legacy-multiselect2-itemvalue-button").alltext_normalized
        )

    def test_selectbutton_aria_label(self):
        mockvalue = mock.MagicMock()
        mockvalue.__str__.return_value = "testvalue"
        if python2_compatibility.is_python2():
            mockvalue.__unicode__.return_value = "testvalue"

        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue).render())
        self.assertEqual(
            'Select "testvalue"', selector.one("button.cradmin-legacy-multiselect2-itemvalue-button")["aria-label"]
        )

    def test_selectbutton_id(self):
        mockvalue = mock.MagicMock()
        mockvalue.pk = 10
        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue).render())
        self.assertTrue(selector.exists("button#cradmin_legacy_multiselect2_selectbutton_10"))

    def test_angularjs_directive(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue).render())
        directiveoptions = json.loads(
            selector.one("button.cradmin-legacy-multiselect2-itemvalue-button")["cradmin-legacy-multiselect2-select"]
        )
        self.assertEqual(
            {
                "custom_data": None,
                "is_selected": False,
                "item_wrapper_css_selector": "li",
                "preview_container_css_selector": ".cradmin-legacy-multiselect2-itemvalue",
                "preview_css_selector": ".cradmin-legacy-multiselect2-selected-item",
                "target_dom_id": "cradmin_legacy_multiselect2_select_target",
            },
            directiveoptions,
        )

    def test_angularjs_directive_custom_target_dom_id(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue, target_dom_id="testid").render())
        directiveoptions = json.loads(
            selector.one("button.cradmin-legacy-multiselect2-itemvalue-button")["cradmin-legacy-multiselect2-select"]
        )
        self.assertEqual("testid", directiveoptions["target_dom_id"])

    def test_angularjs_directive_is_selected_false(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue, is_selected=False).render())
        directiveoptions = json.loads(
            selector.one("button.cradmin-legacy-multiselect2-itemvalue-button")["cradmin-legacy-multiselect2-select"]
        )
        self.assertFalse(directiveoptions["is_selected"])

    def test_angularjs_directive_is_selected_true(self):
        mockvalue = mock.MagicMock()
        selector = htmls.S(listbuilder_itemvalues.ItemValue(value=mockvalue, is_selected=True).render())
        directiveoptions = json.loads(
            selector.one("button.cradmin-legacy-multiselect2-itemvalue-button")["cradmin-legacy-multiselect2-select"]
        )
        self.assertTrue(directiveoptions["is_selected"])


class TestManyToManySelect(test.TestCase):
    def test_sanity(self):
        mockvalue = mock.MagicMock()
        mockvalue.__str__.return_value = "testvalue"
        if python2_compatibility.is_python2():
            mockvalue.__unicode__.return_value = "testvalue"
        mockvalue.pk = "unused"
        selector = htmls.S(listbuilder_itemvalues.ManyToManySelect(value=mockvalue).render())
        self.assertEqual(
            "testvalue", selector.one(".cradmin-legacy-listbuilder-itemvalue-titledescription-title").alltext_normalized
        )

    def test_angularjs_directive_custom_data_value(self):
        mockvalue = mock.MagicMock()
        mockvalue.pk = 21
        selector = htmls.S(listbuilder_itemvalues.ManyToManySelect(value=mockvalue, target_dom_id="testid").render())
        directiveoptions = json.loads(
            selector.one("button.cradmin-legacy-multiselect2-itemvalue-button")["cradmin-legacy-multiselect2-select"]
        )
        self.assertEqual(21, directiveoptions["custom_data"]["value"])

    def test_angularjs_directive_custom_data_preview(self):
        mockvalue = mock.MagicMock()
        mockvalue.pk = "unused"
        mockvalue.__str__.return_value = "testvalue"
        if python2_compatibility.is_python2():
            mockvalue.__unicode__.return_value = "testvalue"
        selector = htmls.S(listbuilder_itemvalues.ManyToManySelect(value=mockvalue, target_dom_id="testid").render())
        directiveoptions = json.loads(
            selector.one("button.cradmin-legacy-multiselect2-itemvalue-button")["cradmin-legacy-multiselect2-select"]
        )
        selector = htmls.S(directiveoptions["custom_data"]["preview"])
        self.assertEqual(
            "testvalue", selector.one(".cradmin-legacy-multiselect2-preview-list-value").alltext_normalized
        )
