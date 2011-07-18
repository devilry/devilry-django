from django.test import TestCase
from django.core.exceptions import ValidationError

from .. import fields


class TestRestfulFields(TestCase):
    def testIntegerWithFallbackField(self):
        intfield = fields.IntegerWithFallbackField(fallbackvalue=10)
        self.assertEquals(intfield.clean(''), 10)
        self.assertEquals(intfield.clean(None), 10)
        self.assertEquals(intfield.clean(5), 5)
        self.assertEquals(intfield.clean('5'), 5)

    def testPositiveIntegerWithFallbackField(self):
        intfield = fields.PositiveIntegerWithFallbackField(fallbackvalue=10)
        self.assertEquals(intfield.clean(''), 10)
        self.assertEquals(intfield.clean(None), 10)
        self.assertEquals(intfield.clean(5), 5)
        self.assertEquals(intfield.clean('5'), 5)
        with self.assertRaises(ValidationError):
            intfield.clean(-5)

    def testBooleanWithFallbackField(self):
        boolfield = fields.BooleanWithFallbackField()
        self.assertFalse(boolfield.clean('0'))
        self.assertTrue(boolfield.clean('1'))
        self.assertFalse(boolfield.clean('False'))
        self.assertTrue(boolfield.clean('True'))

        self.assertFalse(boolfield.clean(''))
        self.assertFalse(boolfield.clean(None))
        self.assertFalse(boolfield.clean('10'))
        self.assertFalse(boolfield.clean('yes'))
        self.assertFalse(boolfield.clean('no'))

    def testCharWithFallbackField(self):
        charfield = fields.CharWithFallbackField(fallbackvalue='tst')
        self.assertEquals(charfield.clean(''), 'tst')
        self.assertEquals(charfield.clean(None), 'tst')
        self.assertEquals(charfield.clean(False), 'False')
        self.assertEquals(charfield.clean(True), 'True')
        self.assertEquals(charfield.clean('Hello world'), 'Hello world')
        self.assertEquals(charfield.clean(10), '10')

    def testJsonListWithFallbackField(self):
        jsonfield = fields.JsonListWithFallbackField(fallbackvalue=['Hello', 'World'])
        self.assertEquals(jsonfield.clean(''), ['Hello', 'World'])
        self.assertEquals(jsonfield.clean(None), ['Hello', 'World'])
        self.assertEquals(jsonfield.clean(5), ['Hello', 'World'])
        self.assertEquals(jsonfield.clean('5'), ['Hello', 'World'])
        self.assertEquals(jsonfield.clean(True), ['Hello', 'World'])
        self.assertEquals(jsonfield.clean('{this: "is a test"}'), ['Hello', 'World'])

        self.assertEquals(jsonfield.clean('["10", 20, true, false, -40]'),
                          ['10', 20, True, False, -40])
        self.assertEquals(jsonfield.clean('[{"a":10, "b":"hello"}, {"x":true, "y":false}]'),
                          [dict(a=10, b="hello"), dict(x=True, y=False)])
