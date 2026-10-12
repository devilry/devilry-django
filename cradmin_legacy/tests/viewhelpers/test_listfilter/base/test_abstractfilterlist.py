import logging
from unittest import mock

import htmls
from django.test import TestCase
from model_bakery import baker

from cradmin_legacy.tests.viewhelpers.cradmin_viewhelpers_testapp.models import (
    FilterTestModel,
)
from cradmin_legacy.viewhelpers.listfilter.base import filtershandler
from cradmin_legacy.viewhelpers.listfilter.base.abstractfilter import AbstractFilter
from cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlist import (
    AbstractFilterList,
)
from cradmin_legacy.viewhelpers.listfilter.base.abstractfilterlistchild import (
    AbstractFilterListChild,
)

filtersep = filtershandler.FiltersHandler.filter_separator


class MinimalFilterGroupChild(AbstractFilterListChild):
    template_name = "cradmin_viewhelpers_testapp/listfilter/minimal-filtergroupchild.django.html"


class MinimalIntFilter(AbstractFilter):
    template_name = "cradmin_viewhelpers_testapp/listfilter/minimal-filtergroupchild.django.html"

    def get_slug(self):
        return "i"

    def clean_value(self, value):
        return int(value)


class MinimalStringFilter(AbstractFilter):
    template_name = "cradmin_viewhelpers_testapp/listfilter/minimal-filtergroupchild.django.html"

    def get_slug(self):
        return "s"


class TestAbstractFilterList(TestCase):
    def test_append(self):
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        testchild = MinimalFilterGroupChild()
        filterlist.append(testchild)
        self.assertEqual([testchild], filterlist.children)
        self.assertEqual(filterlist, testchild.filterlist)

    def test_render(self):
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(MinimalFilterGroupChild())
        filterlist.append(MinimalFilterGroupChild())
        selector = htmls.S(filterlist.render(request=mock.MagicMock()))
        self.assertEqual(2, selector.count("li"))

    def test_set_filters_string_invalid_slug(self):
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        stringfilter = MinimalStringFilter()
        filterlist.append(stringfilter)
        with self.assertLogs(filtershandler.logger, level=logging.DEBUG) as logcontext:
            filterlist.set_filters_string("x-10")
            self.assertEqual(len(logcontext.records), 1)
            self.assertEqual(logcontext.records[0].message, '"x" is not a valid filter slug.')

    def test_set_filters_string(self):
        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        intfilter = MinimalIntFilter()
        stringfilter = MinimalStringFilter()
        filterlist.append(intfilter)
        filterlist.append(stringfilter)
        with self.assertNoLogs(filtershandler.logger, level=logging.DEBUG):
            filterlist.set_filters_string(f"i-10{filtersep}s-test")
        self.assertEqual(["10"], intfilter.values)
        self.assertEqual(["test"], stringfilter.values)

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

        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(FilterOne(slug="filterone"))
        filterlist.append(FilterTwo(slug="filtertwo"))
        queryset = filterlist.filter(FilterTestModel.objects.all())
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

        filterlist = AbstractFilterList(urlbuilder=mock.MagicMock(), target_dom_id="testdomid")
        filterlist.append(FilterOne(slug="filterone"))
        filterlist.append(FilterTwo(slug="filtertwo"))
        queryset = filterlist.filter(FilterTestModel.objects.all(), exclude={"filterone"})
        self.assertEqual({match1, match2}, set(queryset))
