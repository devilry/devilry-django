import json

from django import forms


class DevilryMarkdownWidget(forms.widgets.Textarea):
    template_name = 'devilry_comment/devilry_markdown_editor.django.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({'json_attrs': json.dumps(context['widget']['attrs'])})
        return context
