import re


class AbstractSpec(object):

    @classmethod
    def match(cls, specstring):
        raise NotImplementedError()

    def __init__(self, specstring):
        self.specstring = specstring

    def validate(self, value):
        raise NotImplementedError()

    def __str__(self):
        return self.specstring


class NumberRangeSpec(AbstractSpec):
    patt = re.compile(r"\s*\d+-\d+\s*")

    @classmethod
    def match(cls, specstring):
        return cls.patt.match(specstring)

    def __init__(self, specstring):
        super(NumberRangeSpec, self).__init__(specstring)
        l = specstring.strip().split('-')
        self.start = int(l[0])
        self.end = int(l[1])

    def validate(self, value):
        errmsg = 'Must be a digit between %(start)s and %(end)s' % dict(
                start=self.start, end=self.end)
        if not value.isdigit():
            raise ValueError(errmsg)
        value = int(value)
        if value < self.start or value > self.end:
            raise ValueError(errmsg)
        else:
            return value


class SequenceSpec(AbstractSpec):
    patt = re.compile(r"\s*((?:\w+/)*\w+)\s*")

    @classmethod
    def match(cls, specstring):
        return cls.patt.match(specstring)

    def __init__(self, specstring):
        super(SequenceSpec, self).__init__(specstring)
        self.valid_values = specstring.strip().split('/')

    def validate(self, value):
        if value in self.valid_values:
            return self.valid_values.index(value)
        else:
            raise ValueError('Must be one of: %(values)s' % dict(
                values='/'.join(self.valid_values)))


class Spec(object):
    _spechandlers = []

    @classmethod
    def register_spechandler(cls, spechandler_cls):
        cls._spechandlers.append(spechandler_cls)

    @classmethod
    def parse(cls, specstring):
        for spechandler in cls._spechandlers:
            if spechandler.match(specstring):
                return spechandler(specstring)
        raise ValueError('Invalid format specification: %(format_spec)s.' % \
                dict(format_spec=specstring))


Spec.register_spechandler(NumberRangeSpec)
Spec.register_spechandler(SequenceSpec)
