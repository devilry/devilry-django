import htmls
from django.test import TestCase

from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist import AbstractFilterList
from cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractradio import AbstractRadioFilter


class TestAbstractRadioFilter(TestCase):
    def test_render_sanity(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("first", "First choice"),
                    ("second", "Second choice"),
                    ("third", "Third choice"),
                ]

        testfilter = MyRadioFilter(slug="test")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertTrue(selector.exists("#cradmin_legacy_listfilter_test.cradmin-legacy-listfilter-filter"))
        self.assertTrue(selector.exists("#cradmin_legacy_listfilter_test_input"))
        self.assertEqual(3, selector.count('input[type="radio"]'))

    def test_render_add_value(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("first", "First choice"),
                ]

        testfilter = MyRadioFilter(slug="test")
        testfilter.set_values(values=[])
        filterlist = AbstractFilterList(
            urlbuilder=lambda filters_string: f"/test/{filters_string}", target_dom_id="testdomid"
        )
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("/test/test-first", selector.one('input[type="radio"]')["data-url"])

    def test_render_radio_label(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("somevalue", "Test"),
                ]

        testfilter = MyRadioFilter(slug="test")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual(
            "Test", selector.one("#cradmin_legacy_listfilter_test_input_somevalue_wrapper").alltext_normalized
        )

    def test_render_radio_unchecked(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("somevalue", "Test"),
                ]

        testfilter = MyRadioFilter(slug="test")
        testfilter.set_values(values=[])
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertFalse(selector.one('input[type="radio"]').hasattribute("checked"))

    def test_render_radio_checked(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("somevalue", "Test"),
                ]

        testfilter = MyRadioFilter(slug="test")
        testfilter.set_values(values=["somevalue"])
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertTrue(selector.one('input[type="radio"]').hasattribute("checked"))

    def test_render_label_no_label(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("unused", "unused"),
                ]

        testfilter = MyRadioFilter(slug="test")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertFalse(selector.exists("label#cradmin_legacy_listfilter_test_label"))

    def test_render_label_has_label(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("unused", "unused"),
                ]

        testfilter = MyRadioFilter(slug="test", label="A label")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("A label", selector.one("label#cradmin_legacy_listfilter_test_label").alltext_normalized)

    def test_render_label_get_label_is_screenreader_only_true(self):
        class MyRadioFilter(AbstractRadioFilter):
            def get_choices(self):
                return [
                    ("unused", "unused"),
                ]

            def get_label_is_screenreader_only(self):
                return True

        testfilter = MyRadioFilter(slug="test", label="A label")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertTrue(selector.exists("label#cradmin_legacy_listfilter_test_label"))
        self.assertTrue(selector.one("label#cradmin_legacy_listfilter_test_label").hasclass("sr-only"))
