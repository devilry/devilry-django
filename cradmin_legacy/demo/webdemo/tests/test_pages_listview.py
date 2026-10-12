from django import test
from model_bakery import baker

from cradmin_legacy.demo.webdemo.views import pages_listbuilder
from cradmin_legacy import cradmin_testhelpers


class TesPagesListBuilderView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = pages_listbuilder.PagesListBuilderView

    def test_get(self):
        site = baker.make("webdemo.Site")
        baker.make("webdemo.Page", site=site, title="Test title")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=site)
        self.assertEqual(
            "Test title", mockresponse.selector.one(".cradmin-legacy-listbuilder-itemvalue h2").alltext_normalized
        )

    def test_get_multiple(self):
        """
        Using selector list on multiple values.
        """
        site = baker.make("webdemo.Site")
        baker.make("webdemo.Page", site=site, title="Test title 1")
        baker.make("webdemo.Page", site=site, title="Test title 2")
        baker.make("webdemo.Page", site=site, title="Test title 3")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=site)
        page_list = mockresponse.selector.list(".cradmin-legacy-listbuilder-itemvalue")
        self.assertEqual(3, len(page_list))
