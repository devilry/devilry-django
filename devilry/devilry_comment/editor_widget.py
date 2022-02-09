import json

from django import forms


class DevilryMarkdownWidget(forms.widgets.Textarea):
    template_name = 'devilry_comment/devilry_markdown_editor.django.html'
