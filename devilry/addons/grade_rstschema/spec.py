import re
from xml.sax.saxutils import escape, quoteattr


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

    def add_hint(self, htmltranslator, hint):
        htmltranslator.body.append(
                '<span class="rstschema_field-hint">%s</span>' % escape(hint))

    def create_html_formfield(self, field, field_id, htmltranslator,
            value=None):
        if value:
            val = ' value=%s' % quoteattr(value)
        else:
            val = ''
        htmltranslator.body.append('<input name="%s" size="10"%s />' % (
            field_id, val))
        hint = self.get_hint()
        if hint:
            self.add_hint(htmltranslator, hint)


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
        self.manyvalues = self.end - self.start > 8

    def validate(self, value):
        errmsg = 'Must be a number between %(start)s and %(end)s' % dict(
                start=self.start, end=self.end)
        if not value.isdigit():
            raise ValueError(errmsg)
        value = int(value)
        if value < self.start or value > self.end:
            raise ValueError(errmsg)
        else:
            return value

    def get_hint(self):
        if self.manyvalues:
            return 'A number between %(start)s and %(end)s' % dict(
                    start=self.start, end=self.end)

    def create_html_formfield(self, field, field_id, htmltranslator,
            value=None):
        if self.manyvalues:
            super(NumberRangeSpec, self).create_html_formfield(field,
                    field_id, htmltranslator, value)
        else:
            valid_values = [str(i) for i in range(self.start, self.end+1)]
            SequenceSpec.create_radio_fields(field, field_id, htmltranslator,
                    value, valid_values)


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

    @classmethod
    def create_radio_fields(cls, field, field_id, htmltranslator, value,
            valid_values):
        if value and not value in valid_values:
            value == None
        for i, validvalue in enumerate(valid_values):
            checked = ""
            radioid = '%s_%d' % (field_id, i)
            if value:
                if value == validvalue:
                    checked = ' checked="checked"'
            elif field.default and validvalue == field.default:
                checked = ' checked="checked"'
            
            htmltranslator.body.append('<div class="rstschema_field-radio">')
            htmltranslator.body.append(
                '<input type="radio" id="%s" name="%s" value="%s"%s />' % (
                    radioid, field_id, validvalue, checked))
            htmltranslator.body.append(
                '<label for="%s">%s</label>' % (
                    radioid, validvalue))
            htmltranslator.body.append('</div>')

    def create_html_formfield(self, field, field_id, htmltranslator,
            value=None):
        SequenceSpec.create_radio_fields(field, field_id, htmltranslator,
                value, self.valid_values)
        


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
