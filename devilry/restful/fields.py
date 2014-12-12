import json
from django import forms


class IntegerWithFallbackField(forms.IntegerField):
    def __init__(self, fallbackvalue=0, *args, **kwargs):
        self._fallbackvalue = fallbackvalue
        super(IntegerWithFallbackField, self).__init__(
                required=False, *args, **kwargs)

    def to_python(self, value):
        value = super(IntegerWithFallbackField, self).to_python(value)
        if value == None:
            return self._fallbackvalue
        else:
            return value

class PositiveIntegerWithFallbackField(IntegerWithFallbackField):
    def __init__(self, *args, **kwargs):
        super(PositiveIntegerWithFallbackField, self).__init__(
                min_value=0, *args, **kwargs)


class BooleanWithFallbackField(forms.Field):
    def __init__(self, fallbackvalue=False, *args, **kwargs):
        self._fallbackvalue = fallbackvalue
        super(BooleanWithFallbackField, self).__init__(
                required=False, *args, **kwargs)

    def to_python(self, value):
        if value in ('0', 'False'):
            return False
        elif value in ('1', 'True'):
            return True
        else:
            return self._fallbackvalue


class CharWithFallbackField(forms.CharField):
    def __init__(self, fallbackvalue=None, *args, **kwargs):
        self._fallbackvalue = fallbackvalue
        super(CharWithFallbackField, self).__init__(
                required=False, *args, **kwargs)

    def to_python(self, value):
        value = super(CharWithFallbackField, self).to_python(value)
        if value == '':
            return self._fallbackvalue
        else:
            return value


class JsonListWithFallbackField(forms.CharField):
    def __init__(self, fallbackvalue=[], *args, **kwargs):
        self._fallbackvalue = fallbackvalue
        super(JsonListWithFallbackField, self).__init__(
                required=False, *args, **kwargs)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        else:
            value = super(JsonListWithFallbackField, self).to_python(value)
            if value == '':
                return self._fallbackvalue
            else:
                try:
                    pythonvalue = json.loads(value)
                except ValueError, e:
                    return self._fallbackvalue
                if isinstance(pythonvalue, list):
                    return pythonvalue
                else:
                    return self._fallbackvalue

class RawWithFallbackField(forms.Field):
    def __init__(self, fallbackvalue=None, *args, **kwargs):
        self._fallbackvalue = fallbackvalue
        super(RawWithFallbackField, self).__init__(required=False, *args, **kwargs)

    def to_python(self, value):
        if value == '':
            return self._fallbackvalue
        return value
