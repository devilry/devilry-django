from datetime import datetime
from django.test import TestCase

from devilry.rest.indata import indata, InvalidIndataError
from devilry.rest.indata import bool_indata
from devilry.rest.indata import unicode_indata
from devilry.rest.indata import isoformatted_datetime
from devilry.rest.indata import list_or_tuple_indata
from devilry.rest.indata import dict_indata


class TestIndata(TestCase):
    def test_indata(self):
        class Tst(object):
            @indata(x=int, y=int)
            def tst(self, x, y=100):
                return x + y

        tst = Tst()
        self.assertRaises(InvalidIndataError, tst.tst, x="a", y="b")
        self.assertEquals(tst.tst(x="10", y="20"), 30)
        self.assertEquals(tst.tst(x=10, y="20"), 30)
        self.assertEquals(tst.tst(x=10, y=20), 30)
        self.assertEquals(tst.tst(x=10), 110)
        try:
            tst.tst()
        except InvalidIndataError, e:
            errormsg = unicode(e)
            self.assertEquals(errormsg,
                              ('tst(...) requires 1 arguments (0 given). '
                               'Missing parameters: \'y\', \'x\'. Note that the list '
                               'of missing parameters may contain optional '
                               'parameters. See the docs for this REST api for '
                               'more details.'))
        else:
            self.fail("InvalidIndataError not raised")

    def test_unicode_indata(self):
        self.assertEquals(unicode_indata(u'test'), u'test')
        self.assertEquals(unicode_indata(u'\u00e5ge'.encode('utf-8')), u'\u00e5ge')
        with self.assertRaises(ValueError):
            unicode_indata(None)

    def test_bool_indata(self):
        self.assertEquals(bool_indata(True), True)
        self.assertEquals(bool_indata(False), False)
        self.assertEquals(bool_indata('true'), True)
        self.assertEquals(bool_indata('false'), False)
        with self.assertRaises(ValueError):
            bool_indata(None)

    def test_isoformatted_datetime(self):
        self.assertEquals(isoformatted_datetime("2010-02-10T01:02:03"), datetime(2010, 2, 10, 1, 2, 3))
        self.assertEquals(isoformatted_datetime("2010-2-10T1:2:3"), datetime(2010, 2, 10, 1, 2, 3))
        with self.assertRaises(ValueError):
            isoformatted_datetime("2010-02-10T01:02")
        with self.assertRaises(ValueError):
            isoformatted_datetime(None)
        with self.assertRaises(ValueError):
            isoformatted_datetime(None)

    def test_list_or_tuple_indata(self):
        self.assertEquals(list_or_tuple_indata([1, 2]), [1, 2])
        self.assertEquals(list_or_tuple_indata((1, 2)), (1, 2))
        with self.assertRaises(ValueError):
            list_or_tuple_indata(None)
        with self.assertRaises(ValueError):
            list_or_tuple_indata(set([1, 2]))

    def test_dict_indata(self):
        self.assertEquals(dict_indata({}), {})
        self.assertEquals(dict_indata({'a': 1}), {'a': 1})
        with self.assertRaises(ValueError):
            list_or_tuple_indata(None)
