import json
from django import forms
from django.template.loader import render_to_string


class AceMarkdownWidget(forms.widgets.Textarea):
    template_name = "cradmin_legacy/acemarkdown/widget.django.html"
    directiveconfig = {
        # 'showTextarea': False,
        # 'theme': 'tomorrow'
    }

    @property
    def media(self):
        return forms.Media(
            js=[
                "cradmin_legacy/dist/vendor/js/ace-editor/ace.js",
            ]
        )

    def get_context(self, name, value, attrs):
        attrs = attrs.copy()
        attrs["textarea cradmin-legacy-acemarkdown-textarea"] = ""
        if "required" in attrs:
            attrs["required"] = False
        return {
            "directiveconfig": json.dumps(self.directiveconfig),
            "widget": {"name": name, "value": value, "attrs": attrs},
        }
