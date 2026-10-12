import htmls
from django.test import TestCase

from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist import AbstractFilterList
from cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect import AbstractSelectFilter


class TestAbstractSelectFilter(TestCase):
    def test_render_sanity(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("", "Do not apply"),
                    ("first", "First choice"),
                    ("second", "Second choice"),
                ]

        testfilter = MySelectFilter(slug="test")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertTrue(selector.exists("#cradmin_legacy_listfilter_test.cradmin-legacy-listfilter-filter"))
        self.assertTrue(selector.exists("select#cradmin_legacy_listfilter_test_input"))
        self.assertEqual(3, selector.count("option"))

    def test_render_option_value_empty(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("", "Do not apply"),
                ]

        testfilter = MySelectFilter(slug="test")
        filterlist = AbstractFilterList(
            urlbuilder=lambda filters_string: f"/test/{filters_string}", target_dom_id="testdomid"
        )
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("/test/", selector.one("option")["value"])

    def test_render_option_value_nonempty(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("somevalue", "Test"),
                ]

        testfilter = MySelectFilter(slug="test")
        filterlist = AbstractFilterList(
            urlbuilder=lambda filters_string: f"/test/{filters_string}", target_dom_id="testdomid"
        )
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("/test/test-somevalue", selector.one("option")["value"])

    def test_render_option_label(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("somevalue", "Test"),
                ]

        testfilter = MySelectFilter(slug="test")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("Test", selector.one("option").alltext_normalized)

    def test_render_option_selected(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("", "Do not apply"),
                    ("first", "First choice"),
                    ("second", "Second choice"),
                ]

        testfilter = MySelectFilter(slug="test")
        testfilter.set_values(values=["first"])
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("First choice", selector.one("option[selected]").alltext_normalized)

    def test_render_option_no_value_select_first(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("", "Do not apply"),
                    ("first", "First choice"),
                    ("second", "Second choice"),
                ]

        testfilter = MySelectFilter(slug="test")
        testfilter.set_values(values=[])
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("Do not apply", selector.one("option[selected]").alltext_normalized)

    def test_render_label_no_label(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("unused", "unused"),
                ]

        testfilter = MySelectFilter(slug="test")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertFalse(selector.exists("label"))

    def test_render_label_has_label(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("unused", "unused"),
                ]

        testfilter = MySelectFilter(slug="test", label="A label")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertEqual("A label", selector.one("label").alltext_normalized)
        self.assertEqual("cradmin_legacy_listfilter_test_input", selector.one("label")["for"])

    def test_render_label_get_label_is_screenreader_only_true(self):
        class MySelectFilter(AbstractSelectFilter):
            def get_choices(self):
                return [
                    ("unused", "unused"),
                ]

            def get_label_is_screenreader_only(self):
                return True

        testfilter = MySelectFilter(slug="test", label="A label")
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(testfilter)
        selector = htmls.S(testfilter.render())
        self.assertTrue(selector.exists("label"))
        self.assertTrue(selector.one("label").hasclass("sr-only"))
