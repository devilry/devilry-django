from django.test import TestCase
from model_bakery import baker

from cradmin_legacy.cradmin_testhelpers import TestCaseMixin
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.cradmin_legacy_testapp import models as testmodels


class ListBuilderViewWithoutPaging(listbuilderview.View):
    model = testmodels.SomeItem

    def get_queryset_for_role(self, role):
        return testmodels.SomeItem.objects.all()


class ListBuilderViewWithPaging(ListBuilderViewWithoutPaging):
    paginate_by = 3


class TestListBuilderView(TestCase, TestCaseMixin):
    viewclass = ListBuilderViewWithoutPaging

    def test_empty(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertFalse(mockresponse.selector.exists(".cradmin-legacy-listbuilder-list"))
        self.assertEqual(
            mockresponse.selector.one(".cradmin-legacy-listbuilderview-no-items-message").alltext_normalized,
            "No some items",
        )

    def test_not_empty(self):
        baker.make("cradmin_legacy_testapp.SomeItem", name="Test name")
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertFalse(mockresponse.selector.exists(".cradmin-legacy-listbuilderview-no-items-message"))
        self.assertTrue(mockresponse.selector.exists(".cradmin-legacy-listbuilder-list"))

    def test_item_rendering(self):
        baker.make("cradmin_legacy_testapp.SomeItem", name="Test name")
        mockresponse = self.mock_http200_getrequest_htmls()
        # mockresponse.selector.prettyprint()
        self.assertEqual(1, mockresponse.selector.count(".cradmin-legacy-listbuilder-list li"))
        self.assertEqual(
            "Test name", mockresponse.selector.one(".cradmin-legacy-listbuilder-list li").alltext_normalized
        )


class TestListBuilderPaginationView(TestCase, TestCaseMixin):
    viewclass = ListBuilderViewWithPaging

    def test_paginate_by_singlepage(self):
        baker.make("cradmin_legacy_testapp.SomeItem", _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(3, mockresponse.selector.count(".cradmin-legacy-listbuilder-list li"))
        self.assertFalse(mockresponse.selector.exists("#cradmin_legacy_contentwrapper .cradmin-legacy-loadmorepager"))

    def test_paginate_by_firstpage(self):
        baker.make("cradmin_legacy_testapp.SomeItem", _quantity=8)
        mockresponse = self.mock_http200_getrequest_htmls()
        # mockresponse.selector.one('#cradmin_legacy_contentwrapper').prettyprint()
        self.assertEqual(3, mockresponse.selector.count(".cradmin-legacy-listbuilder-list li"))
        self.assertTrue(mockresponse.selector.exists("#cradmin_legacy_contentwrapper .cradmin-legacy-loadmorepager"))

    def test_paginate_by_middlepage(self):
        baker.make("cradmin_legacy_testapp.SomeItem", _quantity=8)
        mockresponse = self.mock_http200_getrequest_htmls(requestkwargs={"data": {"page": 2}})
        self.assertEqual(3, mockresponse.selector.count(".cradmin-legacy-listbuilder-list li"))
        self.assertTrue(mockresponse.selector.exists("#cradmin_legacy_contentwrapper .cradmin-legacy-loadmorepager"))

    def test_paginate_by_lastpage(self):
        baker.make("cradmin_legacy_testapp.SomeItem", _quantity=8)
        mockresponse = self.mock_http200_getrequest_htmls(requestkwargs={"data": {"page": 3}})
        self.assertEqual(2, mockresponse.selector.count(".cradmin-legacy-listbuilder-list li"))
        self.assertFalse(mockresponse.selector.exists("#cradmin_legacy_contentwrapper .cradmin-legacy-loadmorepager"))
