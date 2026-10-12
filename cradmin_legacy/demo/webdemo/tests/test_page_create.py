from django import test
from model_bakery import baker

from cradmin_legacy.demo.webdemo.views import pages
from cradmin_legacy import cradmin_testhelpers


class TestPageCreateView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    Testing PageCreateView

    .. attribute:: viewclass

        The viewclass to be tested.

    """

    viewclass = pages.PageCreateView

    def test_get_view_title(self):
        """
        Test the view title ('Create Page').
        """
        site = baker.make("webdemo.Site")
        baker.make("webdemo.Page", site=site)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=site)
        view_title = mockresponse.selector.one(".cradmin-legacy-page-header-inner").alltext_normalized

        self.assertEqual("Create Page", view_title)

    def test_get_create_button_text(self):
        """
        Test the button text for creating a page in view ('Create').
        """
        site = baker.make("webdemo.Site", name="Demosite")
        baker.make("webdemo.Page", title="Webpage2", site=site)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=site)
        button_text = mockresponse.selector.one(".btn-primary").alltext_normalized

        self.assertEqual("Create", button_text)

    def test_post_create_all_required_fields_filled(self):
        """
        Gets 302 Found redirect.
        """
        site = baker.make("webdemo.Site")
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=site,
            requestkwargs={
                "data": {
                    "title": "Title text",
                    "intro": "Intro text",
                    "body": "Body text",
                    "publishing_time": "2000-09-09 13:37",
                }
            },
        )
        self.assertEqual(302, mockresponse.response.status_code)
