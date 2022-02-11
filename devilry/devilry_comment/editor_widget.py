import json

from xml.sax.saxutils import quoteattr

from django.utils.translation import pgettext
from django import forms


class DevilryMarkdownWidget(forms.widgets.Textarea):
    template_name = 'devilry_comment/devilry_markdown_editor.django.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['attributes'] = ' '.join(
            f'{key}={quoteattr(value)}'
            for key, value in {
                'name': name,
                'value': value,
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
                            'Bold, <ctrl+b>')
                    },
                    'italic': {
                        'placeholderText': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Add text here'),
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Italic, <ctrl+i>')
                    },
                    'link': {
                        'placeholderText': pgettext(
                            'devilry markdown widget toolbar placeholder text',
                            'Add text here'),
                        'tooltip': pgettext(
                            'devilry markdown widget toolbar tooltip text',
                            'Link, <ctrl+k>')
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
