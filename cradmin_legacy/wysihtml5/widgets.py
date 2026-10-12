from django import forms


class WysiHtmlTextArea(forms.widgets.Textarea):
    template = ""  # TODO: make a template..

    def render(self, name, value, attrs=None):
        baseVal = super().render(name, value, attrs)

        # return render_to_string(template, {'textarea': baseVal}) #TODO: implement this instead on the above
        return f"<div cradmin_legacy_wysihtml>{baseVal}</div>"
