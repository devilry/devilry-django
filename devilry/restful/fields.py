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


class BooleanWithFallbackField(forms.NullBooleanField):
    def __init__(self, fallbackvalue=False, *args, **kwargs):
        self._fallbackvalue = fallbackvalue
        super(BooleanWithFallbackField, self).__init__(
                required=False, *args, **kwargs)

    def to_python(self, value):
        value = super(BooleanWithFallbackField, self).to_python(value)
        if value == None:
            return self._fallbackvalue
        else:
            return value


class CharWithFallbackField(forms.CharField):
    def __init__(self, fallbackvalue=False, *args, **kwargs):
        self._fallbackvalue = fallbackvalue
        super(CharWithFallbackField, self).__init__(
                required=False, *args, **kwargs)

    def to_python(self, value):
        value = super(CharWithFallbackField, self).to_python(value)
        if value == '':
            return self._fallbackvalue
        else:
            return value

class CharListWithFallbackField(CharWithFallbackField):
    def to_python(self, value):
        value = super(CharWithFallbackField, self).to_python(value)
        if value == '':
            return self._fallbackvalue
        else:
            return value.split(',')
