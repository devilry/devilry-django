from django.test import TestCase
from devilry.rest.indata import indata, InvalidIndataError


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