from django import test
from model_bakery import baker

from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy.demo.multiselect2demo.views import productlist


class TestProductListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = productlist.ProductListView

    def test_empty_list(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertTrue(mockresponse.selector.exists(".cradmin-legacy-listing-no-items-message"))
        self.assertFalse(mockresponse.selector.exists(".cradmin-legacy-listbuilder-list"))

    def test_nonempty_list(self):
        baker.make("multiselect2demo.Product")
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertFalse(mockresponse.selector.exists(".cradmin-legacy-listing-no-items-message"))
        self.assertTrue(mockresponse.selector.exists(".cradmin-legacy-listbuilder-list"))

    def test_default_ordering(self):
        baker.make("multiselect2demo.Product", name="A")
        baker.make("multiselect2demo.Product", name="B")
        baker.make("multiselect2demo.Product", name="C")
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(
            "A", mockresponse.selector.one(".cradmin-legacy-listbuilder-list li:nth-child(1) h2").alltext_normalized
        )
        self.assertEqual(
            "B", mockresponse.selector.one(".cradmin-legacy-listbuilder-list li:nth-child(2) h2").alltext_normalized
        )
        self.assertEqual(
            "C", mockresponse.selector.one(".cradmin-legacy-listbuilder-list li:nth-child(3) h2").alltext_normalized
        )
