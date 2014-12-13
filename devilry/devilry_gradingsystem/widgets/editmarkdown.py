from django.template import Context
from django.template.loader import render_to_string
from django.forms.forms import BoundField
from crispy_forms.layout import LayoutObject



class EditMarkdownLayoutObject(LayoutObject):
    template = "devilry_gradingsystem/widgets/editmarkdown.django.html"

    def render(self, form, form_style, context, **kwargs):
        field_instance = form.fields['feedbacktext']
        bound_field = BoundField(form, field_instance, 'feedbacktext')
        #print dir(bound_field)
        context['field'] = bound_field
        return render_to_string(self.template, context)
