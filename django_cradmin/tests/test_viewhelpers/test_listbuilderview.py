from django.test import TestCase
from model_bakery import baker

from django_cradmin.cradmin_testhelpers import TestCaseMixin
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.django_cradmin_testapp import models as testmodels


class ListBuilderViewWithoutPaging(listbuilderview.View):
    model = testmodels.SomeItem

    def get_queryset_for_role(self):
        return testmodels.SomeItem.objects.all().order_by("id")


class ListBuilderViewWithPaging(ListBuilderViewWithoutPaging):
    paginate_by = 3


class TestListBuilderView(TestCase, TestCaseMixin):
    viewclass = ListBuilderViewWithoutPaging

    def test_empty(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertFalse(mockresponse.selector.exists(".test-cradmin-listbuilder-list"))
        self.assertEqual(
            mockresponse.selector.one(".test-cradmin-no-items-message").alltext_normalized, "No some items"
        )

    def test_not_empty(self):
        baker.make("django_cradmin_testapp.SomeItem", name="Test name")
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertFalse(mockresponse.selector.exists(".test-cradmin-no-items-message"))
        self.assertTrue(mockresponse.selector.exists(".test-cradmin-listbuilder-list"))

    def test_item_rendering(self):
        baker.make("django_cradmin_testapp.SomeItem", name="Test name")
        mockresponse = self.mock_http200_getrequest_htmls()
        # mockresponse.selector.prettyprint()
        self.assertEqual(1, mockresponse.selector.count(".test-cradmin-listbuilder-item-frame-renderer"))
        self.assertEqual(
            "Test name", mockresponse.selector.one(".test-cradmin-listbuilder-item-frame-renderer").alltext_normalized
        )


class TestListBuilderPaginationView(TestCase, TestCaseMixin):
    viewclass = ListBuilderViewWithPaging

    def test_paginate_by_singlepage(self):
        baker.make("django_cradmin_testapp.SomeItem", _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(3, mockresponse.selector.count(".test-cradmin-listbuilder-item-frame-renderer"))
        self.assertFalse(mockresponse.selector.exists(".django-cradmin-loadmorepager"))

    def test_paginate_by_firstpage(self):
        baker.make("django_cradmin_testapp.SomeItem", _quantity=8)
        mockresponse = self.mock_http200_getrequest_htmls()
        # mockresponse.selector.one('#django_cradmin_contentwrapper').prettyprint()
        self.assertEqual(3, mockresponse.selector.count(".test-cradmin-listbuilder-item-frame-renderer"))
        self.assertTrue(mockresponse.selector.exists(".django-cradmin-loadmorepager"))

    def test_paginate_by_middlepage(self):
        baker.make("django_cradmin_testapp.SomeItem", _quantity=8)
        mockresponse = self.mock_http200_getrequest_htmls(requestkwargs={"data": {"page": 2}})
        self.assertEqual(3, mockresponse.selector.count(".test-cradmin-listbuilder-item-frame-renderer"))
        self.assertTrue(mockresponse.selector.exists(".django-cradmin-loadmorepager"))

    def test_paginate_by_lastpage(self):
        baker.make("django_cradmin_testapp.SomeItem", _quantity=8)
        mockresponse = self.mock_http200_getrequest_htmls(requestkwargs={"data": {"page": 3}})
        self.assertEqual(2, mockresponse.selector.count(".test-cradmin-listbuilder-item-frame-renderer"))
        self.assertFalse(mockresponse.selector.exists(".django-cradmin-loadmorepager"))
