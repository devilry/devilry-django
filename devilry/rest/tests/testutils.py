from django.test import TestCase
from devilry.rest.error import InvalidParameterTypeError

from devilry.rest.utils import force_paramtypes


class TestUtils(TestCase):
    def test_force_paramtypes(self):
        @force_paramtypes(x=int, y=int)
        def tst(x, y):
            return x + y

        self.assertRaises(InvalidParameterTypeError, tst, "a", "b")
        self.assertEquals(tst("10", "20"), 30)
        self.assertEquals(tst(10, "20"), 30)
        self.assertEquals(tst(10, 20), 30)