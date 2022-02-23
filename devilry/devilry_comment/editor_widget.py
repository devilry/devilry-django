import json

from xml.sax.saxutils import quoteattr

from django.utils.translation import pgettext
from django import forms
from django.urls import reverse


class DevilryMarkdownWidget(forms.widgets.Textarea):
    template_name = 'devilry_comment/devilry_markdown_editor.django.html'

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
    
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
                'labelText': pgettext(
                    'devilry markdown widget',
                    'Comment'
                ),
                'helpText': pgettext(
                    'devilry markdown widget',
                    'Write a comment in markdown format. Use <strong>**text here**</strong> for bold and <em>*text here*</em> for italic.'
                ),
                'markdownGuideLinkText': pgettext(
                    'devilry markdown widget',
                    'Full guide for the markdown we support here'),
                'markdownGuideLinkUrl': '/markdown-help',
                'markdownPreviewButtonText': pgettext(
                    'devilry markdown widget',
                    'Preview'),
                'markdownPreviewUrl': self._get_preview_markdown_api_url(),
                'markdownPreviewEnabled': 'true' if self.preview_enabled else 'false',
                'markdownPreviewConfig': json.dumps({
                    'editorActiveButtonText': pgettext(
                        'devilry markdown widget',
                        'Preview'),
                    'previewActiveButtonText': pgettext(
                        'devilry markdown widget',
                        'Write'),
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
                    }
                })
            }.items()
        )
        return context


class DevilryMarkdownNoPreviewWidget(DevilryMarkdownWidget):
    @property
    def preview_enabled(self):
        return False