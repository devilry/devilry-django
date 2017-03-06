import json

from django.template.loader import render_to_string
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget


class Default(AceMarkdownWidget):
    template_name = 'devilry_cradmin/devilry_acemarkdown.django.html'
    extra_css_classes = ''

    def get_template_context_data(self):
        return {
            'directiveconfig': json.dumps(self.directiveconfig),
            'extra_css_classes': self.extra_css_classes
        }

    def render(self, name, value, attrs=None):
        attrs = attrs.copy()
        attrs['textarea django-cradmin-acemarkdown-textarea'] = ''
        textarea = super(AceMarkdownWidget, self).render(name, value, attrs)
        context = self.get_template_context_data()
        context['textarea'] = textarea
        return render_to_string(
            self.template_name, context)


class Large(Default):
    """
    Large ace markdown widget.
    """
    extra_css_classes = 'devilry-ace-editor--large'


class Small(Default):
    """
    Small ace markdown widget.
    """
    extra_css_classes = 'devilry-ace-editor--small'
