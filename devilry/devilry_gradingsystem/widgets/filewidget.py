from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class FeedbackEditorFileWidget(forms.ClearableFileInput):
    """
    Clearable file widget.

    Can be made un-clearable (for required fields) using the
    ``clearable`` argument for ``__init__``.
    """
    template_name = 'devilry_gradingsystem/widgets/feedbackeditorfilewidget.django.html'

    def __init__(self, feedbackfile, attrs=None):
        self.feedbackfile = feedbackfile
        super(FeedbackEditorFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        input_html = forms.FileInput.render(self, name, value, attrs)
        output = render_to_string(self.template_name, {
            'input_html': input_html,
            'feedbackfile': self.feedbackfile,
            'clear_checkbox_name': self.clear_checkbox_name(name)
        })
        return mark_safe(output)
