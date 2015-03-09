from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.test import TestCase
import json

from devilry.thirdpartylibs.djangorestframework.views import View


class MockView(View):
    """Mock resource which simply returns a URL, so that we can ensure that reversed URLs are fully qualified"""
    permissions = ()

    def get(self, request):
        return reverse('another')

urlpatterns = patterns('',
    url(r'^$', MockView.as_view()),
    url(r'^another$', MockView.as_view(), name='another'),
)


class ReverseTests(TestCase):
    """Tests for """
    urls = 'devilry.thirdpartylibs.djangorestframework.tests.reverse'

    def test_reversed_urls_are_fully_qualified(self):
        response = self.client.get('/')
        self.assertEqual(json.loads(response.content), 'http://testserver/another')
