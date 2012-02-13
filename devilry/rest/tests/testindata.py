from django.test import TestCase
from devilry.rest.indata import indata, InvalidIndataError
from devilry.rest.indata import none_or_unicode
from devilry.rest.indata import none_or_bool


class TestIndata(TestCase):
    def test_indata(self):
        class Tst(object):
            @indata(x=int, y=int)
            def tst(self, x, y):
                return x + y

        tst = Tst()
        self.assertRaises(InvalidIndataError, tst.tst, x="a", y="b")
        self.assertEquals(tst.tst(x="10", y="20"), 30)
        self.assertEquals(tst.tst(x=10, y="20"), 30)
        self.assertEquals(tst.tst(x=10, y=20), 30)

    def test_unicode_or_none(self):
        self.assertEquals(none_or_unicode(None), None)
        self.assertEquals(none_or_unicode(u'myunicodestring'), u'myunicodestring')
        self.assertEquals(none_or_unicode(u'\u00e5ge'), u'\u00e5ge')
        self.assertEquals(none_or_unicode('mybytestring'), u'mybytestring')
        self.assertEquals(none_or_unicode(u'\u00e5ge'.encode('utf-8')), u'\u00e5ge')
        with self.assertRaises(ValueError):
            none_or_unicode(u'\u00e5ge'.encode('latin-1'))
        with self.assertRaises(ValueError):
            none_or_unicode(True)

    def test_bool_or_none(self):
        self.assertEquals(none_or_bool(None), None)
        self.assertEquals(none_or_bool(True), True)
        self.assertEquals(none_or_bool(False), False)
        with self.assertRaises(ValueError):
            none_or_bool('1')
        with self.assertRaises(ValueError):
            none_or_bool('')
        with self.assertRaises(ValueError):
            none_or_bool(1)
        with self.assertRaises(ValueError):
            none_or_bool(0)
