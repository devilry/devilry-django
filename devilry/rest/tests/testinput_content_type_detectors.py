from django.test import TestCase
from devilry.rest.input_content_type_detectors import parse_content_type


class TestInputContentTypeDetectors(TestCase):
    def test_parse_content_type(self):
        self.assertEquals(parse_content_type('text/html; charset=UTF-8'), ('text/html', 'UTF-8'))
        self.assertEquals(parse_content_type('text/html'), ('text/html', None))
