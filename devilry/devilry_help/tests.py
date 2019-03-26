from django.urls import reverse
from django.test import TestCase
import htmls


class TestHelpView(TestCase):
    def setUp(self):
        self.url = reverse('devilry-help')

    def test_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_organization_specific_documentation_url(self):
        with self.settings(DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL='http://docs.example.com'):
            selector = htmls.S(self.client.get(self.url).content)
            self.assertTrue(selector.exists('#devilry_help_organization_specific_documentation'))
            self.assertEqual(
                selector.one('#devilry_help_organization_specific_documentation a')['href'],
                'http://docs.example.com')

    def test_no_organization_specific_documentation_url(self):
        with self.settings(DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL=None):
            selector = htmls.S(self.client.get(self.url).content)
            self.assertFalse(selector.exists('#devilry_help_organization_specific_documentation'))

    def test_organization_specific_documentation_text(self):
        with self.settings(
                DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL='http://docs.example.com',
                DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_TEXT='A test text'):
            selector = htmls.S(self.client.get(self.url).content)
            self.assertEqual(
                selector.one('#devilry_help_organization_specific_documentation').alltext_normalized,
                'A test text')

    def test_no_organization_specific_documentation_text(self):
        with self.settings(
                DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL='http://docs.example.com'):
            selector = htmls.S(self.client.get(self.url).content)
            self.assertEqual(
                selector.one('#devilry_help_organization_specific_documentation').alltext_normalized,
                'Documentation provided by your organization.')
