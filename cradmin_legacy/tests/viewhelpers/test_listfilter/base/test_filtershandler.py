import logging

from django.test import TestCase
from model_bakery import baker

from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.tests.viewhelpers.cradmin_viewhelpers_testapp.models import (
    FilterTestModel,
)
from cradmin_legacy.viewhelpers.listfilter.base.abstractfilter import AbstractFilter
from cradmin_legacy.viewhelpers.listfilter.base.exceptions import (
    InvalidFiltersStringError,
)
from cradmin_legacy.viewhelpers.listfilter.base.filtershandler import (
    FiltersHandler,
    logger,
)

filtersep = FiltersHandler.filter_separator


class MinimalIntFilter(AbstractFilter):
    def get_slug(self):
        return "i"

    def clean_value(self, value):
        return int(value)


class MinimalStringFilter(AbstractFilter):
    def get_slug(self):
        return "s"


class TestFiltersHandler(TestCase):
    def test_split_raw_filter_values(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        self.assertEqual(["a/b", "c,d"], filtershandler.split_raw_filter_values("a%252Fb%2Cc%252Cd"))

    def test_join_filter_values(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        self.assertEqual("a%252Fb%2Cc%252Cd", filtershandler.join_filter_values(["a/b", "c,d"]))

    def test_invalid_filter_string(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        with self.assertRaisesMessage(InvalidFiltersStringError, '"x" does not contain "-".'):
            filtershandler.parse("x")

    def test_invalid_filter_slug(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        with self.assertLogs(logger, level=logging.DEBUG) as logcontext:
            filtershandler.parse("x-10")
            self.assertEqual(len(logcontext.records), 1)
            self.assertEqual(logcontext.records[0].message, '"x" is not a valid filter slug.')

    def test_add_filter_duplicate_filter_slug(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(AbstractFilter(slug="x"))
        with self.assertRaisesMessage(ValueError, 'Duplicate slug: "x".'):
            filtershandler.add_filter(AbstractFilter(slug="x"))

    def test_add_filter_invalid_filter_slug(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        with self.assertRaisesMessage(ValueError, 'Invalid filter slug: "x-y". Slugs can not contain "-".'):
            filtershandler.add_filter(AbstractFilter(slug="x-y"))

    def test_parse_empty_string(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.parse("")
        self.assertEqual({}, filtershandler.filtermap)

    def test_parse_none(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.parse(None)
        self.assertEqual({}, filtershandler.filtermap)

    def test_parse_simple_valid_filter_string(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalStringFilter())
        filtershandler.parse("s-test")
        with self.assertNoLogs(logger, level=logging.DEBUG):
            self.assertEqual(["test"], filtershandler.filtermap["s"].values)

    def test_parse_multivalue_valid_filter_string(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalStringFilter())
        filtershandler.parse("s-a,b,c")
        self.assertEqual(["a", "b", "c"], filtershandler.filtermap["s"].values)

    def test_parse_simple_valid_filter_string_trailing_filtersep(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalStringFilter())
        filtershandler.parse(f"s-test{filtersep}")
        self.assertEqual(["test"], filtershandler.filtermap["s"].values)

    def test_parse_simple_valid_filter_string_leading_filtersep(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalStringFilter())
        filtershandler.parse(f"{filtersep}s-test")
        self.assertEqual(["test"], filtershandler.filtermap["s"].values)

    def test_parse_simple_valid_filter_string_trailing_slug_and_value_separator(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalStringFilter())
        filtershandler.parse("s-")
        self.assertEqual([""], filtershandler.filtermap["s"].values)

    def test_parse_complex_valid_filter_string(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalStringFilter())
        filtershandler.add_filter(MinimalIntFilter())
        filtershandler.parse(f"{filtersep}i-10{filtersep}s-jane,joe{filtersep}")
        self.assertEqual(2, len(filtershandler.filtermap))
        self.assertEqual(["10"], filtershandler.filtermap["i"].values)
        self.assertEqual(["jane", "joe"], filtershandler.filtermap["s"].values)

    def test_build_filters_string(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        intfilter = MinimalIntFilter()
        intfilter.set_values(values=["10"])
        stringfilter = MinimalStringFilter()
        stringfilter.set_values(values=["jane", "joe"])
        filtershandler.add_filter(intfilter)
        filtershandler.add_filter(stringfilter)

        new_stringfilter = stringfilter.copy()
        new_stringfilter.set_values(values=["jack", "peter"])
        self.assertEqual(
            f"i-10{filtersep}s-jack%2Cpeter", filtershandler.build_filters_string(changed_filterobject=new_stringfilter)
        )

    def test_build_filter_url(self):
        def urlbuilder(filters_string):
            return f"{filtersep}the{filtersep}prefix{filtersep}{filters_string}?a=querystring"

        filtershandler = FiltersHandler(urlbuilder=urlbuilder)
        intfilter = MinimalIntFilter()
        intfilter.set_values(values=["10"])
        stringfilter = MinimalStringFilter()
        stringfilter.set_values(values=["jane", "joe"])
        filtershandler.add_filter(intfilter)
        filtershandler.add_filter(stringfilter)

        new_stringfilter = stringfilter.copy()
        new_stringfilter.set_values(values=["jack", "peter"])
        self.assertEqual(
            f"{filtersep}the{filtersep}prefix{filtersep}i-10{filtersep}s-jack%2Cpeter?a=querystring",
            filtershandler.build_filter_url(changed_filterobject=new_stringfilter),
        )

    def test_filter(self):
        class FilterOne(AbstractFilter):
            def filter(self, queryobject):
                return queryobject.filter(mycharfield="test")

        class FilterTwo(AbstractFilter):
            def filter(self, queryobject):
                return queryobject.filter(mybooleanfield=True)

        match = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="test", mybooleanfield=True)
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="no match", mybooleanfield=True)
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="test", mybooleanfield=False)

        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(FilterOne(slug="filterone"))
        filtershandler.add_filter(FilterTwo(slug="filtertwo"))
        queryset = filtershandler.filter(FilterTestModel.objects.all())
        self.assertEqual({match}, set(queryset))

    def test_filter_exclude(self):
        class FilterOne(AbstractFilter):
            def filter(self, queryobject):
                return queryobject.filter(mycharfield="test")

        class FilterTwo(AbstractFilter):
            def filter(self, queryobject):
                return queryobject.filter(mybooleanfield=True)

        match1 = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="test", mybooleanfield=True)
        match2 = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="no match", mybooleanfield=True)
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="test", mybooleanfield=False)

        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(FilterOne(slug="filterone"))
        filtershandler.add_filter(FilterTwo(slug="filtertwo"))
        queryset = filtershandler.filter(FilterTestModel.objects.all(), exclude={"filterone"})
        self.assertEqual({match1, match2}, set(queryset))

    def test_get_label_for(self):
        class MyFilter(AbstractFilter):
            pass

        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MyFilter(label="Test Label", slug="test"))
        self.assertEqual("Test Label", filtershandler.get_label_for("test"))

    def test_get_cleaned_value_for(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalIntFilter())
        filtershandler.parse(f"{filtersep}i-10")
        self.assertEqual(10, filtershandler.get_cleaned_value_for("i"))

    def test_get_cleaned_values_for(self):
        filtershandler = FiltersHandler(urlbuilder=mock.MagicMock())
        filtershandler.add_filter(MinimalIntFilter())
        filtershandler.parse(f"{filtersep}i-10")
        self.assertEqual([10], filtershandler.get_cleaned_values_for("i"))
