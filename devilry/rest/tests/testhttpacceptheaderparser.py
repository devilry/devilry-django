import re
from django.test import TestCase
from devilry.rest.httpacceptheaderparser import HttpAcceptHeaderParser, MediaRange


class TestParseHttpHeader(TestCase):
    def test_typeregex(self):
        regex = '^' + HttpAcceptHeaderParser.type_regex + '$'
        self.assertTrue(bool(re.match(regex, "text")))
        self.assertTrue(bool(re.match(regex, "conference-info+xml")))
        self.assertTrue(bool(re.match(regex, "*")))
        self.assertFalse(bool(re.match(regex, "**")))
        self.assertFalse(bool(re.match(regex, "invalid type")))
        self.assertFalse(bool(re.match(regex, "/test")))
        self.assertFalse(bool(re.match(regex, "test/")))

    def test_mediarangeregex(self):
        regex = '^' + HttpAcceptHeaderParser.typeandsubtype_regex + '$'
        self.assertTrue(bool(re.match(regex, "text/html")))
        self.assertTrue(bool(re.match(regex, "text/html+xml")))
        self.assertTrue(bool(re.match(regex, "text/*")))
        self.assertTrue(bool(re.match(regex, "*/*")))
        self.assertTrue(bool(re.match(regex, "*/html")))
        self.assertFalse(bool(re.match(regex, " text/html")))
        self.assertFalse(bool(re.match(regex, "text/html;")))

    def test_paramregex(self):
        regex = '^' + HttpAcceptHeaderParser.params_regex + '$'
        self.assertTrue(bool(re.match(regex, ";q=1.0")))
        self.assertTrue(bool(re.match(regex, ";q=0.0")))
        self.assertTrue(bool(re.match(regex, ";q=0.1")))
        self.assertTrue(bool(re.match(regex, ";q=1")))
        self.assertFalse(bool(re.match(regex, ";q=1.1")))
        self.assertFalse(bool(re.match(regex, "q=1.0")))

    def test_mediarangepatt(self):
        found = HttpAcceptHeaderParser.mediarange_patt.findall(
            "text/html,application/xhtml+xml,application/xml;q=0.7,*/*;q=0.8,text/plain")
        self.assertEqual(found, [
            ('text', 'html', ''),
            ('application', 'xhtml+xml', ''),
            ('application', 'xml', '0.7'),
            ('*', '*', '0.8'),
            ('text', 'plain', '')]
        )

    def test_parse_content_type(self):
        self.assertEqual(HttpAcceptHeaderParser.parse_content_type('text/html'), ('text', 'html'))

    def test_parse(self):
        p = HttpAcceptHeaderParser()
        p.parse("text/html,text/plain;q=0.9,*/*;q=0.2,application/xml;q=0.6,application/xhtml+xml")
        self.assertEquals(p.mediaranges[0].ttype, 'text')
        self.assertEquals(p.mediaranges[0].subtype, 'html')
        self.assertEquals(p.mediaranges[1].ttype, 'application')
        self.assertEquals(p.mediaranges[1].subtype, 'xhtml+xml')
        self.assertEquals(p.mediaranges[2].ttype, 'text')
        self.assertEquals(p.mediaranges[2].subtype, 'plain')
        self.assertEquals(p.mediaranges[3].ttype, 'application')
        self.assertEquals(p.mediaranges[3].subtype, 'xml')
        self.assertEquals(p.mediaranges[4].ttype, '*')
        self.assertEquals(p.mediaranges[4].subtype, '*')

    def test_mediarangematch(self):
        self.assertTrue(MediaRange('text', 'plain', 1).match(('text', 'plain')))
        self.assertTrue(MediaRange('*', 'plain', 1).match(('text', 'plain')))
        self.assertTrue(MediaRange('text', '*', 1).match(('text', 'plain')))
        self.assertTrue(MediaRange('*', '*', 1).match(('text', 'plain')))

    def test_sort(self):
        p = HttpAcceptHeaderParser()
        p._add('*', '*', '')
        p._add('text', '*', '')
        p._add('text', 'html', '')
        p._sort()
        self.assertEquals(p.mediaranges[0].subtype, 'html')
        self.assertEquals(p.mediaranges[2].subtype, '*')

    def test_match(self):
        p = HttpAcceptHeaderParser()
        p._add('*', '*', '')
        p._add('text', '*', '')
        p._add('text', 'html', '')
        p._sort()
        self.assertEqual(p.match('text/xml', 'text/html'), 'text/html')
        self.assertEqual(p.match('text/unspecified'), 'text/unspecified', msg="text/* does not match")
        self.assertEqual(p.match('tst/tst'), 'tst/tst', msg="*/* does not match")