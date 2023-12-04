import json

from xml.sax.saxutils import quoteattr

from django.utils.translation import pgettext
from django import forms
from django.urls import reverse


class DevilryMarkdownWidget(forms.widgets.Textarea):
    template_name = 'devilry_comment/devilry_markdown_editor.django.html'

    def __init__(self, *args, label='', request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label = label or pgettext('devilry markdown widget', 'Comment text')
    
    @property
    def preview_enabled(self):
        return True

    def _get_preview_markdown_api_url(self):
        if self.request:
            return f'{self.request.scheme}://{self.request.get_host()}{reverse("devilry_comment_api_preview_markdown")}'
        return ''

    def get_context(self, name, value, attrs):
        value = value or ''
        context = super().get_context(name, value, attrs)
        context['attributes'] = ' '.join(
            f'{key}={quoteattr(value)}'
            for key, value in {
                'name': name,
                'value': value,
                'placeholder': pgettext(
                    'devilry markdown widget',
                    'Write your comment here'
                ),
                'labelText': self.label,
                'helpText': pgettext(
                    'devilry markdown widget',
                    'Write a comment in markdown format. Use <strong>**text here**</strong> for bold and <em>*text here*</em> for italic.'
                ),
                'markdownGuideLinkText': pgettext(
                    'devilry markdown widget',
                    'Here you can get an overview of the supported Markdown.'),
                'markdownGuideLinkUrl': '/markdown-help',
                'markdownPreviewConfig': json.dumps({
                    'editorActiveButtonText': pgettext(
                        'devilry markdown widget',
                        'Write'),
                    'previewActiveButtonText': pgettext(
                        'devilry markdown widget',
                        'Preview'),
                    'previewApiErrorMessage': pgettext(
                        'devilry markdown widget',
                        'Something went wrong.'
                    ),
                    'previewApiFetchingMessage': pgettext(
                        'devilry markdown widget',
                        'Preparing preview'
                    ),
                    'apiUrl': self._get_preview_markdown_api_url(),
                    'enabled': self.preview_enabled
                }),
                'toolbarConfig': json.dumps({
                    'heading': {
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Heading')
                    },
                    'bold': {
                        'placeholderText': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Add text here'),
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Bold')
                    },
                    'italic': {
                        'placeholderText': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Add text here'),
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Italic')
                    },
                    'link': {
                        'placeholderText': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Add text here'),
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Link')
                    },
                    'codeInline': {
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Code')
                    },
                    'codeBlock': {
                        'placeholderText': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Programminglanguage'),
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Code-block')
                    },
                    'unorderedList': {
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Bulleted list')
                    },
                    'orderedList': {
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Numbered list')
                    },
                    'image': {
                        'placeholderTextTitle': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Src \'Title\''),
                        'placeholderTextDescription': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Add description here'),
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Image')
                    }
                })
            }.items()
        )
        return context


class DevilryMarkdownNoPreviewWidget(DevilryMarkdownWidget):
    @property
    def preview_enabled(self):
        return False