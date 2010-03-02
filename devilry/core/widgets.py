from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.utils import formats
from django import forms


class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        hidden_attrs = {'name': name, 'type': 'hidden'}
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            hidden_attrs['value'] = force_unicode(formats.localize_input(value))
        return mark_safe(u'<input%s /><div%s>%s</div>' % (
                flatatt(hidden_attrs),
                flatatt(self.build_attrs(attrs)),
                conditional_escape(force_unicode(value))))
