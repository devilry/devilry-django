from urllib.parse import urlsplit

from django.http import QueryDict
from django.test import TestCase

from cradmin_legacy import urlutils


class TestUpdateQuerystring(TestCase):
    def test_simple(self):
        self.assertEqual(
            urlutils.update_querystring("http://example.com", {"next": "http://example.com/admin"}),
            "http://example.com?next=http%3A%2F%2Fexample.com%2Fadmin",
        )

    def test_update_existing(self):
        self.assertEqual(
            urlutils.update_querystring("http://example.com?next=/test", {"next": "/updated"}),
            "http://example.com?next=%2Fupdated",
        )

    def test_keep_existing(self):
        url = urlutils.update_querystring("http://example.com?next=/test", {"other": "otherstuff"})
        url_split = urlsplit(url)
        querydict = QueryDict(url_split.query)
        self.assertEqual(
            querydict.dict(),
            {
                "next": "/test",
                "other": "otherstuff",
            },
        )

    def test_ignore_none_values(self):
        self.assertEqual(urlutils.update_querystring("http://example.com", {"next": None}), "http://example.com")

    def test_do_not_ignore_none_values(self):
        self.assertEqual(
            urlutils.update_querystring("http://example.com", {"next": None}, ignore_none_values=False),
            "http://example.com?next=None",
        )
