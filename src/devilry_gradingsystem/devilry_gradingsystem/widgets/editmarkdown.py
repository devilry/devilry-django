# from django import forms
# from django.utils.html import escape
# from django.forms.util import flatatt
# from django.template.loader import render_to_string
# from django.utils.encoding import StrAndUnicode, force_unicode
# from django.utils.safestring import mark_safe


# class EditMarkdownWidget(forms.Widget):
#     class Media:
#         js = (
#             'devilry_gradingsystem/components/ace-builds/src-min-noconflict/ace.js',
#             'devilry_gradingsystem/js/editmarkdownwidget.js'
#         )

#     template = 'devilry_gradingsystem/widgets/editmarkdownwidget.django.html'

#     def __init__(self, attrs=None):
#         super(EditMarkdownWidget, self).__init__(attrs=attrs)

#     def render(self, name, value, attrs=None):
#         if value is None:
#             value = ''
#         final_attrs = self.build_attrs(attrs, name=name,
#             style='display: none;')
#         id = final_attrs['id']
#         return mark_safe(render_to_string(self.template, {
#             'widgetid': '{}_widget'.format(id),
#             'attrs': flatatt(final_attrs),
#             'value': force_unicode(value),
#         }))


from django.template import Context
from django.template.loader import render_to_string
from django.forms.forms import BoundField
from crispy_forms.layout import LayoutObject



class EditMarkdownLayoutObject(LayoutObject):
    template = "devilry_gradingsystem/widgets/editmarkdown.django.html"

    def render(self, form, form_style, context, **kwargs):
        field_instance = form.fields['feedbacktext']
        bound_field = BoundField(form, field_instance, 'feedbacktext')
        print dir(bound_field)
        return render_to_string(self.template, Context({
            'field': bound_field
        }))